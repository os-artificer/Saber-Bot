"""
Dev / OSS RSS source configuration.
"""

from __future__ import annotations

from typing import Any, Dict, List

LANG_SOURCES: Dict[str, Dict[str, Any]] = {
    "python": {"name": "Python", "url": "https://blog.python.org/feeds/posts/default", "icon": "🐍", "org": "Python Software Foundation", "desc": "通用编程语言，数据科学/AI首选", "region": "overseas"},
    "rust": {"name": "Rust", "url": "https://blog.rust-lang.org/feed.xml", "icon": "🦀", "org": "Rust Foundation", "desc": "系统编程语言，主打内存安全", "region": "overseas"},
    "typescript": {"name": "TypeScript", "url": "https://devblogs.microsoft.com/typescript/feed/", "icon": "📘", "org": "Microsoft", "desc": "JavaScript超集，静态类型", "region": "overseas"},
    "nodejs": {"name": "Node.js", "url": "https://nodejs.org/en/feed/blog.xml", "icon": "🟢", "org": "OpenJS Foundation", "desc": "JavaScript运行时", "region": "overseas"},
    "golang": {"name": "Go", "url": "https://go.dev/blog/index.xml", "icon": "🔵", "org": "Google", "desc": "Google开发的编译型语言", "region": "overseas"},
    "java": {"name": "Java", "url": "https://www.oracle.com/java/technologies/javadoc-and-docs.html", "icon": "☕", "org": "Oracle / OpenJDK", "desc": "企业级后端开发", "region": "overseas"},
    "ruby": {"name": "Ruby", "url": "https://ruby.social/@RubyWeekly/feed", "icon": "💎", "org": "Ruby Association", "desc": "简洁web开发语言", "region": "overseas"},
    "swift": {"name": "Swift", "url": "https://swift.org/blog/swift-5.9-released/", "icon": "🍎", "org": "Apple", "desc": "iOS/macOS开发语言", "region": "overseas"},
    "kotlin": {"name": "Kotlin", "url": "https://blog.jetbrains.com/kotlin/feed/", "icon": "🟣", "org": "JetBrains / Google", "desc": "JVM语言，Android首选", "region": "overseas"},
    "csharp": {"name": "C#", "url": "https://devblogs.microsoft.com/dotnet/feed/", "icon": "💜", "org": "Microsoft", "desc": ".NET平台主语言", "region": "overseas"},
}

OSS_SOURCES: Dict[str, Dict[str, Any]] = {
    "github": {"name": "GitHub Blog", "url": "https://github.com/blog.atom", "icon": "🐙", "desc": "全球最大代码托管平台动态", "region": "overseas"},
    "producthunt": {"name": "Product Hunt", "url": "https://www.producthunt.com/feed", "icon": "🚀", "desc": "新产品与工具发布", "region": "overseas"},
    "infoq_feed": {"name": "InfoQ（聚合 feed）", "url": "https://feed.infoq.com/", "icon": "📚", "desc": "InfoQ 英文站聚合 RSS", "region": "overseas"},
    "thenewstack": {"name": "The New Stack", "url": "https://thenewstack.io/feed/", "icon": "☁️", "desc": "云原生与基础设施", "region": "overseas"},
    "oschina": {"name": "OSCHINA", "url": "https://www.oschina.net/news/rss", "icon": "🐼", "desc": "中文开源技术资讯", "region": "china"},
    "docker": {"name": "Docker Blog", "url": "https://blog.docker.com/feed/", "icon": "🐳", "desc": "容器化技术领导者", "region": "overseas"},
    "kubernetes": {"name": "Kubernetes", "url": "https://kubernetes.io/feed.xml", "icon": "☸️", "desc": "容器编排平台", "region": "overseas"},
    "spring": {"name": "Spring", "url": "https://spring.io/blog.atom", "icon": "🌱", "desc": "Java企业级框架", "region": "overseas"},
    "react": {"name": "React", "url": "https://react.dev/blog/rss.xml", "icon": "⚛️", "desc": "UI构建库", "region": "overseas"},
    "vue": {"name": "Vue.js", "url": "https://blog.vuejs.org/feed.xml", "icon": "💚", "desc": "渐进式前端框架", "region": "overseas"},
    "deno": {"name": "Deno", "url": "https://deno.com/blog/rss.xml", "icon": "🦕", "desc": "安全 JS/TS 运行时", "region": "overseas"},
    "svelte": {"name": "Svelte", "url": "https://svelte.dev/blog/rss.xml", "icon": "🔥", "desc": "编译型前端框架", "region": "overseas"},
    "angular": {"name": "Angular", "url": "https://blog.angular.io/feed.atom", "icon": "📐", "desc": "Google前端框架", "region": "overseas"},
    "linux": {"name": "Linux", "url": "https://lkml.org/lkml/recent.xml", "icon": "🐧", "desc": "开源内核", "region": "overseas"},
    "vscode": {"name": "VS Code", "url": "https://code.visualstudio.com/feed.xml", "icon": "📎", "desc": "微软轻量级编辑器", "region": "overseas"},
    "postgresql": {"name": "PostgreSQL", "url": "https://www.postgresql.org/blogs/rss/", "icon": "🐘", "desc": "开源关系型数据库", "region": "overseas"},
}

DEV_SOURCES: Dict[str, Dict[str, Any]] = {
    "devto": {"name": "dev.to", "url": "https://dev.to/feed", "icon": "👨‍💻", "desc": "开发者社区博客", "region": "overseas"},
    "hackernews": {"name": "Hacker News（首页）", "url": "https://hnrss.org/frontpage", "icon": "👾", "desc": "HN 热门（hnrss frontpage）", "region": "overseas"},
    "hn_show": {"name": "Hacker News（Show）", "url": "https://hnrss.org/show", "icon": "🎬", "desc": "HN Show 分区", "region": "overseas"},
    "kr36": {"name": "36氪", "url": "https://36kr.com/feed", "icon": "⚡", "desc": "科技与创业热点", "region": "china"},
    "lobsters": {"name": "Lobsters", "url": "https://lobste.rs/rss", "icon": "🦞", "desc": "技术社区", "region": "overseas"},
}

ALL_SOURCES: Dict[str, Dict[str, Any]] = {}
ALL_SOURCES.update(LANG_SOURCES)
ALL_SOURCES.update(OSS_SOURCES)
ALL_SOURCES.update(DEV_SOURCES)

DEV_LANG_ORDER: List[str] = ["python", "rust", "typescript", "nodejs", "golang", "java", "kotlin", "csharp", "swift", "ruby"]
DEV_OSS_ORDER: List[str] = ["github", "producthunt", "infoq_feed", "thenewstack", "oschina", "docker", "kubernetes", "spring", "react", "vue", "angular", "deno", "svelte", "linux", "vscode", "postgresql"]
DEV_COMM_ORDER: List[str] = ["devto", "hackernews", "hn_show", "kr36", "lobsters"]
