#!/usr/bin/env python3
"""
academic_search.py — 四源学术论文搜索工具
支持 arXiv + OpenAlex + Crossref + Semantic Scholar（有 key 时加入）

数据源概览:
  arXiv      — CS/ML/Physics 预印本，更新最快，无需 key
  OpenAlex   — 4.74亿篇全学科，完全免费，无需注册
  Crossref   — 1.4亿篇 DOI 元数据，精确引用关系，无需 key
  S2         — 2.14亿篇，语义搜索强（需 key，无 key 时常限流）

用法:
  python3 academic_search.py "whisper speech recognition" [--limit 5]
  python3 academic_search.py "neural machine translation" --year-from 2022
  python3 academic_search.py --doi "10.1145/3442188.3445922"
  python3 academic_search.py "TTS prosody" --sources arxiv,openalex,crossref,s2

配置（可选）:
  环境变量 S2_API_KEY     — Semantic Scholar API key（无 key 时 S2 自动跳过）
  环境变量 OPENALEX_EMAIL — OpenAlex polite pool（默认: openclaw@research.local）

返回格式: JSON，包含 papers 列表和 source_stats
"""

import sys
import os
import json
import time
import argparse
import re
import urllib.request
import urllib.parse
import urllib.error

# ── 配置 ──────────────────────────────────────────────────────────────────────
S2_API_KEY    = os.environ.get("S2_API_KEY", "")
OA_EMAIL      = os.environ.get("OPENALEX_EMAIL", "openclaw@research.local")
DEFAULT_LIMIT = 8
REQUEST_DELAY = 0.4   # arXiv 建议 3 req/s

# ── 工具函数 ──────────────────────────────────────────────────────────────────
def _get(url, params=None, headers=None, retries=3, timeout=20):
    """简单 HTTP GET，不依赖 requests（纯标准库兜底）"""
    try:
        import requests as _req
        r = _req.get(url, params=params, headers=headers or {}, timeout=timeout)
        return r.status_code, r.text, dict(r.headers)
    except ImportError:
        pass

    # 纯标准库实现
    if params:
        qs = urllib.parse.urlencode(params, doseq=True)
        url = f"{url}?{qs}"
    req = urllib.request.Request(url, headers=headers or {})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read().decode("utf-8"), dict(resp.headers)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 ** attempt * 2)
                continue
            return e.code, str(e), {}
        except Exception as e:
            return 0, str(e), {}
    return 0, "max retries exceeded", {}


def _clean(text, maxlen=200):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text[:maxlen] + "…" if len(text) > maxlen else text


# ── arXiv ─────────────────────────────────────────────────────────────────────
def search_arxiv(query, limit=DEFAULT_LIMIT, year_from=None):
    """搜索 arXiv，返回标准化论文列表"""
    time.sleep(REQUEST_DELAY)
    url = "https://export.arxiv.org/api/query"
    
    # 构造查询：标题+摘要搜索
    q = query.replace(" ", "+")
    search_query = f"all:{q}"
    if year_from:
        search_query += f"+AND+submittedDate:[{year_from}01010000+TO+99991231235900]"
    
    params = {
        "search_query": search_query,
        "max_results": limit,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    status, body, _ = _get(url, params=params)
    if status != 200:
        return [], f"arXiv HTTP {status}"
    
    papers = []
    entries = re.findall(r"<entry>(.*?)</entry>", body, re.DOTALL)
    for entry in entries:
        def tag(t): 
            m = re.search(rf"<{t}[^>]*>(.*?)</{t}>", entry, re.DOTALL)
            return m.group(1).strip() if m else ""
        
        arxiv_id_raw = tag("id")
        arxiv_id = re.search(r"abs/(.+?)$", arxiv_id_raw)
        arxiv_id = arxiv_id.group(1) if arxiv_id else arxiv_id_raw
        
        year_m = re.search(r"<published>(\d{4})", entry)
        year = int(year_m.group(1)) if year_m else None
        
        authors = re.findall(r"<name>(.*?)</name>", entry)
        
        papers.append({
            "source": "arXiv",
            "id": arxiv_id,
            "title": _clean(tag("title"), 150),
            "abstract": _clean(tag("summary"), 300),
            "year": year,
            "authors": authors[:4],
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf": f"https://arxiv.org/pdf/{arxiv_id}",
            "cited_by": None,
            "doi": None
        })
    
    return papers, None


# ── OpenAlex ──────────────────────────────────────────────────────────────────
def search_openalex(query, limit=DEFAULT_LIMIT, year_from=None):
    """搜索 OpenAlex（4.74亿篇，完全免费，无需注册）"""
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "mailto": OA_EMAIL,
        "per-page": min(limit, 25),
        "select": "title,publication_year,cited_by_count,authorships,abstract_inverted_index,doi,id,primary_location",
        "sort": "relevance_score:desc"
    }
    if year_from:
        params["filter"] = f"publication_year:>{year_from - 1}"
    
    status, body, hdrs = _get(url, params=params)
    if status != 200:
        return [], f"OpenAlex HTTP {status}"
    
    try:
        data = json.loads(body)
    except Exception as e:
        return [], f"OpenAlex JSON parse error: {e}"
    
    papers = []
    for item in data.get("results", []):
        # 重建摘要（OpenAlex 用倒排索引存储）
        abstract = ""
        inv = item.get("abstract_inverted_index")
        if inv:
            word_pos = []
            for word, positions in inv.items():
                for pos in positions:
                    word_pos.append((pos, word))
            word_pos.sort()
            abstract = " ".join(w for _, w in word_pos)
        
        doi = item.get("doi", "")
        if doi:
            doi = doi.replace("https://doi.org/", "")
        
        authors = []
        for auth in item.get("authorships", [])[:4]:
            name = auth.get("author", {}).get("display_name", "")
            if name:
                authors.append(name)
        
        loc = item.get("primary_location") or {}
        pdf_url = loc.get("pdf_url", "")
        landing = loc.get("landing_page_url", "")
        
        papers.append({
            "source": "OpenAlex",
            "id": item.get("id", "").replace("https://openalex.org/", ""),
            "title": _clean(item.get("title", ""), 150),
            "abstract": _clean(abstract, 300),
            "year": item.get("publication_year"),
            "authors": authors,
            "url": landing or (f"https://doi.org/{doi}" if doi else ""),
            "pdf": pdf_url,
            "cited_by": item.get("cited_by_count"),
            "doi": doi
        })
    
    return papers, None


# ── Crossref ──────────────────────────────────────────────────────────────────
def search_crossref(query, limit=DEFAULT_LIMIT, year_from=None):
    """搜索 Crossref（1.4亿篇 DOI 元数据，完全免费，无需注册）"""
    time.sleep(REQUEST_DELAY)
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": min(limit, 20),
        "sort": "relevance",
        "order": "desc",
        # polite pool：加 mailto 获得更高优先级和更稳定的响应
        "mailto": OA_EMAIL,
        "select": "DOI,title,abstract,author,published,is-referenced-by-count,link,container-title,type"
    }
    if year_from:
        params["filter"] = f"from-pub-date:{year_from}"

    headers = {
        "User-Agent": f"OpenclawResearch/1.0 (mailto:{OA_EMAIL})"
    }

    status, body, _ = _get(url, params=params, headers=headers)
    if status != 200:
        return [], f"Crossref HTTP {status}"

    try:
        data = json.loads(body)
    except Exception as e:
        return [], f"Crossref JSON parse error: {e}"

    papers = []
    items = data.get("message", {}).get("items", [])
    for item in items:
        # 标题
        title_list = item.get("title", [])
        title = title_list[0] if title_list else ""
        if not title:
            continue

        # 摘要（部分记录有，去 HTML 标签）
        abstract = item.get("abstract", "")
        if abstract:
            abstract = re.sub(r"<[^>]+>", "", abstract)

        # 作者
        authors = []
        for a in item.get("author", [])[:4]:
            given = a.get("given", "")
            family = a.get("family", "")
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)

        # 年份：优先用 published，其次 published-print
        year = None
        for date_field in ("published", "published-print", "published-online"):
            dp = item.get(date_field, {}).get("date-parts", [[]])
            if dp and dp[0]:
                year = dp[0][0]
                break

        # 过滤年份
        if year_from and year and year < year_from:
            continue

        doi = item.get("DOI", "")

        # 开放获取 PDF 链接
        pdf_url = ""
        for link in item.get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL", "")
                break

        # 引用次数
        cited = item.get("is-referenced-by-count")

        # 期刊/会议名
        container = item.get("container-title", [])
        venue = container[0] if container else ""

        papers.append({
            "source": "Crossref",
            "id": doi,
            "title": _clean(title, 150),
            "abstract": _clean(abstract, 300),
            "year": year,
            "authors": authors,
            "url": f"https://doi.org/{doi}" if doi else "",
            "pdf": pdf_url,
            "cited_by": cited,
            "doi": doi,
            "venue": venue
        })

    return papers, None


# ── Semantic Scholar ──────────────────────────────────────────────────────────
def search_s2(query, limit=DEFAULT_LIMIT, year_from=None, api_key=None):
    """搜索 Semantic Scholar（有 key 100 req/s，无 key 降速重试）"""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    
    params = {
        "query": query,
        "limit": min(limit, 100),
        "fields": "title,abstract,year,authors,citationCount,externalIds,openAccessPdf"
    }
    if year_from:
        params["year"] = f"{year_from}-"
    
    # 无 key 时加延迟降低限流概率
    if not api_key:
        time.sleep(1.5)
    
    status, body, _ = _get(url, params=params, headers=headers)
    
    if status == 429:
        if not api_key:
            # 无 key 遇到 429，退避重试一次
            time.sleep(5)
            status, body, _ = _get(url, params=params, headers=headers)
        if status == 429:
            return [], "Semantic Scholar 限流 (429) — 建议申请免费 API key: https://www.semanticscholar.org/product/api"
    
    if status != 200:
        return [], f"Semantic Scholar HTTP {status}"
    
    try:
        data = json.loads(body)
    except Exception as e:
        return [], f"S2 JSON parse error: {e}"
    
    papers = []
    for item in data.get("data", []):
        ext_ids = item.get("externalIds", {}) or {}
        doi = ext_ids.get("DOI", "")
        arxiv_id = ext_ids.get("ArXiv", "")
        
        pdf_info = item.get("openAccessPdf") or {}
        pdf_url = pdf_info.get("url", "")
        
        authors = [a.get("name", "") for a in item.get("authors", [])[:4]]
        
        papers.append({
            "source": "Semantic Scholar",
            "id": item.get("paperId", ""),
            "title": _clean(item.get("title", ""), 150),
            "abstract": _clean(item.get("abstract", "") or "", 300),
            "year": item.get("year"),
            "authors": authors,
            "url": f"https://www.semanticscholar.org/paper/{item.get('paperId','')}",
            "pdf": pdf_url or (f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else ""),
            "cited_by": item.get("citationCount"),
            "doi": doi
        })
    
    return papers, None


# ── 搜索指定 DOI ──────────────────────────────────────────────────────────────
def search_by_doi(doi):
    """通过 DOI 获取论文详情（同时查 OpenAlex + Crossref + S2）"""
    results = {}

    # OpenAlex by DOI
    url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi, safe='')}"
    status, body, _ = _get(url, params={"mailto": OA_EMAIL})
    if status == 200:
        try:
            results["openalex"] = json.loads(body)
        except Exception:
            pass

    # Crossref by DOI
    url_cr = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    headers_cr = {"User-Agent": f"OpenclawResearch/1.0 (mailto:{OA_EMAIL})"}
    time.sleep(0.3)
    status_cr, body_cr, _ = _get(url_cr, headers=headers_cr)
    if status_cr == 200:
        try:
            cr_data = json.loads(body_cr)
            results["crossref"] = cr_data.get("message", cr_data)
        except Exception:
            pass

    # S2 by DOI（有 key 时才查，避免无 key 限流）
    if S2_API_KEY:
        url2 = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
        headers = {"x-api-key": S2_API_KEY}
        params = {"fields": "title,abstract,year,authors,citationCount,references,citations"}
        time.sleep(0.5)
        status2, body2, _ = _get(url2, params=params, headers=headers)
        if status2 == 200:
            try:
                results["s2"] = json.loads(body2)
            except Exception:
                pass

    return results


# ── 主函数 ────────────────────────────────────────────────────────────────────
def deduplicate(papers):
    """按 DOI 和标题去重"""
    seen_dois = set()
    seen_titles = set()
    out = []
    for p in papers:
        doi = (p.get("doi") or "").strip().lower()
        title = re.sub(r"[^a-z0-9]", "", (p.get("title") or "").lower())[:60]
        
        if doi and doi in seen_dois:
            continue
        if title and title in seen_titles:
            continue
        
        if doi:
            seen_dois.add(doi)
        if title:
            seen_titles.add(title)
        out.append(p)
    return out


def main():
    parser = argparse.ArgumentParser(description="四源学术论文搜索: arXiv + OpenAlex + Crossref + Semantic Scholar")
    parser.add_argument("query", nargs="?", help="搜索关键词")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="每源返回数量 (默认 8)")
    parser.add_argument("--sources", default="arxiv,openalex,crossref", help="启用的数据源，逗号分隔 (默认: arxiv,openalex,crossref；可加 s2)")
    parser.add_argument("--year-from", type=int, default=None, dest="year_from", help="论文年份下限")
    parser.add_argument("--doi", default=None, help="按 DOI 精确查找（查 OpenAlex + Crossref + S2）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式（供程序解析）")
    parser.add_argument("--s2-key", default=S2_API_KEY, dest="s2_key", help="Semantic Scholar API key（可选）")

    args = parser.parse_args()

    if args.doi:
        result = search_by_doi(args.doi)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    sources = [s.strip() for s in args.sources.split(",")]
    all_papers = []
    errors = {}
    source_counts = {}

    if "arxiv" in sources:
        papers, err = search_arxiv(args.query, args.limit, args.year_from)
        if err:
            errors["arXiv"] = err
        all_papers.extend(papers)
        source_counts["arXiv"] = len(papers)

    if "openalex" in sources:
        papers, err = search_openalex(args.query, args.limit, args.year_from)
        if err:
            errors["OpenAlex"] = err
        all_papers.extend(papers)
        source_counts["OpenAlex"] = len(papers)

    if "crossref" in sources:
        papers, err = search_crossref(args.query, args.limit, args.year_from)
        if err:
            errors["Crossref"] = err
        all_papers.extend(papers)
        source_counts["Crossref"] = len(papers)

    if "s2" in sources:
        papers, err = search_s2(args.query, args.limit, args.year_from, api_key=args.s2_key or None)
        if err:
            errors["Semantic Scholar"] = err
        all_papers.extend(papers)
        source_counts["Semantic Scholar"] = len(papers)

    # 去重 + 排序（有引用数的优先）
    all_papers = deduplicate(all_papers)
    all_papers.sort(key=lambda p: (p.get("cited_by") or -1), reverse=True)

    if args.json:
        output = {
            "query": args.query,
            "total": len(all_papers),
            "source_stats": source_counts,
            "errors": errors,
            "papers": all_papers
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 人类可读输出
    print(f"\n{'='*65}")
    print(f"学术搜索结果: {args.query}")
    print(f"{'='*65}")
    print(f"数据源统计: {source_counts}")
    if errors:
        for src, err in errors.items():
            print(f"⚠️  {src}: {err}")
    print(f"去重后共 {len(all_papers)} 篇\n")

    for i, p in enumerate(all_papers, 1):
        cited = f"被引 {p['cited_by']}" if p.get('cited_by') is not None else "引用数未知"
        year = p.get("year", "?")
        authors_str = ", ".join(p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors_str += " et al."
        venue = f" | {p['venue']}" if p.get("venue") else ""

        print(f"[{i}] [{p['source']}] ({year}) {p['title']}{venue}")
        print(f"     作者: {authors_str}")
        print(f"     {cited}  |  {p['url']}")
        if p.get("abstract"):
            print(f"     摘要: {p['abstract'][:180]}...")
        if p.get("pdf"):
            print(f"     PDF: {p['pdf']}")
        print()

    if not all_papers:
        print("未找到结果，请尝试换关键词或扩大时间范围")


if __name__ == "__main__":
    main()
