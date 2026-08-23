# Workflow Cooperation Maps

Generated: map_workflow_cooperation.py
Total workflows documented: 4

## Overview

This document maps how skills cooperate within 4 parallel workflows. Each workflow represents an independent pipeline for different creative/technical purposes.

### The 4 Parallel Workflows

1. **Writing Workflow (内容创作)** (25 skills)
   - Research → Write → Refine → Distribute pipeline for content creation

1. **配图 Workflow (Illustration/Visual)** (29 skills)
   - Generate → Enhance → Export pipeline for visual content

1. **剪辑 Workflow (Video Editing)** (11 skills)
   - Transcribe → Edit → Generate → Optimize pipeline for video production

1. **网站 Workflow (Website Development)** (38 skills)
   - Design → Code → Test → Deploy pipeline for web development

---

## Writing Workflow (内容创作)

**Description:** Research → Write → Refine → Distribute pipeline for content creation

**Total skills:** 25

### Workflow Phases

#### Research (5 skills)

**honest-deep-researcher**
- A research specialist that prioritizes factual accuracy, data validation, and transparent reporting....
- Connects to: google-deep-research, competitive-ads-extractor

**google-deep-research**
- Conduct deep research using Google NotebookLM (and optionally Gemini Web). Automates web searching, ...

**web-search-manager**
- Unified web search with Brave Search (2,000/month) + SerpAPI fallback (100/month). Privacy-focused, ...

**youtube-research-video-topic**
- Conduct pure research for YouTube video topics by analyzing competitors, identifying content gaps, a...
- Connects to: youtube-plan-new-video

**competitive-ads-extractor**
- Extracts and analyzes competitors' ads from ad libraries (Facebook, LinkedIn, etc.) to understand wh...

#### Write (6 skills)

**content-research-writer**
- Assists in writing high-quality content by conducting research, adding citations, improving hooks, i...

**my-creative-writer**
- 一个通用的、可学习用户风格的“去 AI 味”写作助手。它不局限于特定风格，而是通过分析用户的过往作品建立“风格指纹”，并结合严格的“反 AI 腔”法则（拒绝陈词滥调、教科书结构），产出极具人情味、叙事...

**psychological-copywriter**
- Generates high-value marketing copy using psychological principles like "Premium Anchoring" and "Men...

**performance-ads-writer**
- Writes high-conversion ads for Google Ads and Meta Ads (Facebook/Instagram). Performs deep research ...

**interview-to-article**
- An interactive interview agent that acts as a reporter/editor to extract your thoughts and ghostwrit...

**general-song-writer**
- Hit songwriter agent. Generates catchy, emotional, and memorable lyrics (hooks/spreadable points) an...

#### Refine (3 skills)

**naturalize-text-localize**
- 全语言通用翻译与文本人性化。用于跨语言翻译、润色或改写任何语言的文本，重点在于使其地道、自然，移除 AI 味（套话、免责声明、过渡词），并通过简化词汇、短句化、情感细节和受众对齐来提升可信度。

**simplify**
- No description

**reverse-prompt-engineer**
- Generates detailed AI image generation prompts from descriptions or analysis of images/content. Use ...

#### Distribute (7 skills)

**youtube-title**
- Generate optimized YouTube video titles that maximize click-through rates by sparking curiosity and ...
- Connects to: youtube-thumbnail

**youtube-video-hook**
- Skill for creating optimized YouTube video opening hooks (first 5-30 seconds) that maximize viewer r...

**youtube-plan-new-video**
- Generate a complete video plan with optimized title, thumbnail, and hook concepts based on research....
- Connects to: youtube-thumbnail, youtube-title, youtube-research-video-topic, youtube-video-hook

**youtube-thumbnail**
- Skill for creating and editing Youtube thumbnails that are optimized for click-through rate. This sk...

**xhs-note-creator-template**
- 小红书笔记素材创作技能。当用户需要创建小红书笔记素材时使用这个技能。技能包含：根据用户的需求和提供的资料，撰写小红书笔记内容（标题+正文），生成图片卡片（封面+正文卡片），以及发布小红书笔记。

**local-store-promotion**
- 本地实体门店全渠道推广技能。适用于餐饮、婚纱、美容、零售等本地商家，覆盖小红书/抖音/微信/大众点评/美团等平台的内容策划、发布节奏、活动设计与数据复盘。

**Post-Social-Media-With-GetLate-API-Repurpose-Distribute**
- Automate social media posting via GetLate API. Use this skill when the user wants to post images or ...

#### Specialized (4 skills)

**seven-figure-course-builder**
- Complete SOP for building, launching, and scaling seven-figure online courses. Use when the user wan...

**japan-med-content-matrix**
- Strategy and content generator for Japan Medical/Insurance niche. Use for creating product matrices,...

**creator-monetization-engine**
- Comprehensive global creator monetization framework with multi-platform distribution, team-based con...
- Connects to: content-research-writer, youtube-thumbnail, youtube-title, performance-ads-writer

**internal-comms**
- A set of resources to help me write all kinds of internal communications, using the formats that my ...

### Common Cooperation Chains

1. **Deep Research → Content Writing**
   - `honest-deep-researcher` → `content-research-writer` → `my-creative-writer`
   - Research findings feed directly into content creation

2. **Content → Platform Distribution**
   - `my-creative-writer` → `youtube-title` + `youtube-thumbnail` → `Post-Social-Media-With-GetLate-API-Repurpose-Distribute`
   - Single content piece adapted for multiple platforms

3. **Interview → Article**
   - `interview-to-article` → `naturalize-text-localize` → platform-specific skills
   - Interview transcripts transformed into polished articles

### Entry Points

**Where to start in this workflow:**

- **honest-deep-researcher**: A research specialist that prioritizes factual accuracy, data validation, and transparent reporting....
- **google-deep-research**: Conduct deep research using Google NotebookLM (and optionally Gemini Web). Automates web searching, ...
- **web-search-manager**: Unified web search with Brave Search (2,000/month) + SerpAPI fallback (100/month). Privacy-focused, ...

### Integration Points

**How this workflow connects to others:**

- **→ 配图**: Content needs illustrations (`smart-illustrator`, `article-broll-illustrator`)
- **→ 剪辑**: Written scripts become video content (`remotion`, `sora2-video-gen`)
- **→ 网站**: Content published on websites (`wp-site-manager`, `stitch`)

---

## 配图 Workflow (Illustration/Visual)

**Description:** Generate → Enhance → Export pipeline for visual content

**Total skills:** 29

### Workflow Phases

#### Generate (9 skills)

**smart-illustrator**
- 智能配图与 PPT 信息图生成器。支持三种模式：(1) 文章配图模式 - 分析文章内容，生成插图；(2) PPT/Slides 模式 - 生成批量信息图；(3) Cover 模式 - 生成封面图。所有...

**Nano-Banana**
- High-performance image generation using Nano Banana Pro (Gemini 3 Pro Image / 3.1 Flash Image). Use ...

**seedream-4-5**
- Advanced 4K image generation and semantic editing (material changes, pose preservation) using Seedre...

**sora2-video-gen**
- Generate videos using the Sora 2 model via APIMart. Use this skill when the user wants to create vid...

**svg-generator**
- Generates high-quality, scalable vector graphics (SVG) code for icons, diagrams, and illustrations. ...

**svg-icon-search**
- Search for elegant SVG icons (Lucide, Phosphor, Simple Icons) using the Iconify API. Returns raw SVG...

**reference-photo-expander**
- Generates a series of consistent photos based on a single reference photo. Maintains subject identit...

**article-broll-illustrator**
- Generate consistent, timeline-mapped B-roll images for YouTube videos. Analyzes video scripts (text/...
- Connects to: visual-prompt-engineer-patten

**theme-serial-gen**
- Generate a consistent series of images (default 4) based on a theme/topic using Nano Banana Pro. Use...

#### Enhance (6 skills)

**image-enhancer**
- Improves the quality of images, especially screenshots, by enhancing resolution, sharpness, and clar...

**topaz-photo-ai-upscaler**
- Professional AI-powered image upscaling using Topaz Photo AI CLI. Better quality than Upscayl for ca...

**repair-old-photos**
- Restore and repair old, damaged, or low-quality photos. Use when the user provides an old photo and ...

**ecommerce-product-refine**
- 电商产品精修与白底图制作专家。拥有 5 年电商产品精修经验，专精美妆、厨具、服饰、数码等全品类。当用户需要处理产品图片，进行材质优化、去瑕疵、生成符合电商标准的纯净白底图（RGB:255,255,25...

**remove-bg**
- Removes white backgrounds from images to create transparent PNGs. Use this for logos, product shots,...

**gemini-watermark-remover**
- Watermark removal toolkit — Gemini invisible watermark, NotebookLM PDF/image, Seedance/Douyin video,...

#### Design Systems (5 skills)

**mermaid-visualizer**
- Transform text content into professional Mermaid diagrams for presentations and documentation. Use w...

**excalidraw-diagram**
- Generate Excalidraw diagrams from text content for Obsidian. Use when user asks to create diagrams, ...

**obsidian-canvas-creator**
- Create Obsidian Canvas files from text content, supporting both MindMap and freeform layouts. Use th...

**obsidian-json-canvas**
- Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when wor...

**theme-factory**
- Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML la...

#### Specialized (7 skills)

**youtube-thumbnail**
- Skill for creating and editing Youtube thumbnails that are optimized for click-through rate. This sk...

**opc-banner-creator**
- Create banners using AI image generation. Discuss format/style, generate variations, iterate with us...

**opc-logo-creator**
- Create logos using AI image generation. Discuss style/ratio, generate variations, iterate with user ...

**ecommerce-kv**
- 电商营销海报(KV)生成专家。当用户需要为产品生成带有模特、特定场景、营销文案的高级宣传海报时使用。智能分析产品属性，自动匹配模特与场景，全程严格保持产品原始结构。

**aippt-enterprise**
- AIPPT - 基于模板定制化生成 PPT。垫图约束风格 → Kie's Nano Banana 2 (Flash) 替换内容 → Antigravity IDE 生成每一页 → 打包 PPTX。

**reverse-prompt-engineer**
- Generates detailed AI image generation prompts from descriptions or analysis of images/content. Use ...

**visual-prompt-engineer-patten**
- 专业的 AI 视频/图像提示词工程师 (Visual Prompt Engineer)，专注于 Seedance 2.0 (即梦/Dreamina) 等先进视频模型的提示词生成与优化。擅长运镜控制、分...

#### Format Conversion (2 skills)

**heif-converter**
- Expert tool for converting HEIF/HIF images to compatible formats (PNG/JPG) while managing color prof...

**document-skills**
- Professional toolkit for PDF manipulation, Excel financial modeling, Word redlining/OOXML, and PPT a...

### Common Cooperation Chains

1. **Generate → Enhance → Export**
   - `smart-illustrator` / `seedream-4-5` → `image-enhancer` → `remove-bg`
   - AI generation followed by quality enhancement

2. **Photo Restoration Pipeline**
   - `repair-old-photos` → `topaz-photo-ai-upscaler` → final export
   - Restore damaged photos then upscale for modern use

3. **Consistent Series Generation**
   - `reference-photo-expander` / `theme-serial-gen` → `image-enhancer`
   - Generate consistent image series for branding

### Entry Points

**Where to start in this workflow:**

- **smart-illustrator**: 智能配图与 PPT 信息图生成器。支持三种模式：(1) 文章配图模式 - 分析文章内容，生成插图；(2) PPT/Slides 模式 - 生成批量信息图；(3) Cover 模式 - 生成封面图。所有...
- **Nano-Banana**: High-performance image generation using Nano Banana Pro (Gemini 3 Pro Image / 3.1 Flash Image). Use ...
- **seedream-4-5**: Advanced 4K image generation and semantic editing (material changes, pose preservation) using Seedre...

### Integration Points

**How this workflow connects to others:**

- **← Writing**: Illustrations support written content
- **→ 剪辑**: Images become video B-roll or thumbnails
- **→ 网站**: Visual assets deployed to websites

---

## 剪辑 Workflow (Video Editing)

**Description:** Transcribe → Edit → Generate → Optimize pipeline for video production

**Total skills:** 11

### Workflow Phases

#### Transcribe (2 skills)

**transcribe-media**
- Transcribe video or audio files into text using Google's Gemini 3 Flash. Preserves original language...

**Read-Media-Gemini**
- A specialized skill for Gemini 3 Flash and other models via Antigravity Local Proxy. Optimized for m...

#### Edit (3 skills)

**videocut**
- Comprehensive video editing agent. Expert in transcribing, detecting bloopers/silences, generating r...

**gyroflow-stabilizer**
- Stabilize video footage (especially Sony S-Log3 with gyro data) using Gyroflow CLI. Supports batch p...

**music-video-prep**
- Professional music video quality assurance and guidance skill. Acts as an audio engineering consulta...
- Connects to: transcribe-media, gyroflow-stabilizer

#### Generate (4 skills)

**remotion**
- Generate walkthrough videos from Stitch projects using Remotion with smooth transitions, zooming, an...

**remotion-ads-producer**
- Create programmatic video ads using Remotion (React-based video framework). Best for SaaS, structure...
- Connects to: remotion

**sora2-video-gen**
- Generate videos using the Sora 2 model via APIMart. Use this skill when the user wants to create vid...

**manim-math-animator**
- Generate high-quality mathematical animations and visualizations using the Manim (Community Edition)...

#### Optimize (2 skills)

**gemini-watermark-remover**
- Watermark removal toolkit — Gemini invisible watermark, NotebookLM PDF/image, Seedance/Douyin video,...

**video-downloader**
- Download YouTube videos with customizable quality and format options. Use this skill when the user a...

### Common Cooperation Chains

1. **Transcribe → Edit → Export**
   - `transcribe-media` → `videocut` → final video
   - Transcription drives intelligent editing decisions

2. **Stabilize → Edit → Generate**
   - `gyroflow-stabilizer` → `videocut` → `remotion`
   - Fix shaky footage before editing and effects

3. **Programmatic Video Generation**
   - `stitch` → `remotion` / `remotion-ads-producer`
   - Design system feeds into programmatic video creation

### Entry Points

**Where to start in this workflow:**

- **transcribe-media**: Transcribe video or audio files into text using Google's Gemini 3 Flash. Preserves original language...
- **Read-Media-Gemini**: A specialized skill for Gemini 3 Flash and other models via Antigravity Local Proxy. Optimized for m...

### Integration Points

**How this workflow connects to others:**

- **← Writing**: Scripts and content feed video production
- **← 配图**: Visual assets used in video editing
- **→ 网站**: Videos embedded in web projects

---

## 网站 Workflow (Website Development)

**Description:** Design → Code → Test → Deploy pipeline for web development

**Total skills:** 38

### Workflow Phases

#### Design (8 skills)

**stitch**
- Unified router for all Stitch workflows. Use when the user wants to design UI, generate pages, conve...
- Connects to: stitch-enhance-prompt, design-md, stitch-design-md, stitch-loop

**stitch-loop**
- Teaches agents to iteratively build websites using Stitch with an autonomous baton-passing loop patt...
- Connects to: design-md, stitch, stitch-design-md

**stitch-enhance-prompt**
- Transforms vague UI ideas into polished, Stitch-optimized prompts. Enhances specificity, adds UI/UX ...
- Connects to: design-md, stitch, stitch-design-md, stitch-loop

**stitch-react-components**
- Converts Stitch designs into modular Vite and React components using system-level networking and AST...
- Connects to: stitch

**stitch-design-md**
- Analyze Stitch projects and synthesize a semantic design system into DESIGN.md files
- Connects to: stitch

**design-md**
- Analyze Stitch projects and synthesize a semantic design system into DESIGN.md files
- Connects to: stitch

**frontend-design**
- Create distinctive, production-grade frontend interfaces with high design quality. Use this skill wh...

**web-design-guidelines**
- Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check acc...

#### WordPress (15 skills)

**wp-cli-expert**
- Expert WordPress management using WP-CLI. Use when the user wants to manage WordPress sites via comm...

**wp-wpcli-and-ops**
- Use when working with WP-CLI (wp) for WordPress operations: safe search-replace, db export/import, p...

**wp-site-manager**
- Generic WordPress site management — deploy pages, manage media, execute WP-CLI remotely, site operat...
- Connects to: wp-block-themes, wp-block-development, wp-rest-api, wp-plugin-development, wp-cli-expert, chrome-devtools, wp-phpstan, wp-interactivity-api, wordpress-router, wp-performance

**wp-project-triage**
- Use when you need a deterministic inspection of a WordPress repository (plugin/theme/block theme/WP ...

**wp-block-development**
- Use when developing WordPress (Gutenberg) blocks: block.json metadata, register_block_type(_from_met...
- Connects to: wp-project-triage, wp-interactivity-api

**wp-block-themes**
- Use when developing WordPress block themes: theme.json (global settings/styles), templates and templ...
- Connects to: wp-project-triage

**wp-plugin-development**
- Use when developing WordPress plugins: architecture and hooks, activation/deactivation/uninstall, ad...
- Connects to: wp-project-triage

**wp-rest-api**
- Use when building, extending, or debugging WordPress REST API endpoints/routes: register_rest_route,...
- Connects to: wp-project-triage

**wp-interactivity-api**
- Use when building or debugging WordPress Interactivity API features (data-wp-* directives, @wordpres...
- Connects to: wp-project-triage

**wp-performance**
- Use when investigating or improving WordPress performance (backend-only agent): profiling and measur...

**wp-phpstan**
- Use when configuring, running, or fixing PHPStan static analysis in WordPress projects (plugins/them...
- Connects to: wp-project-triage

**wp-playground**
- Use for WordPress Playground workflows: fast disposable WP instances in the browser or locally via @...

**wpds**
- Use when building UIs leveraging the WordPress Design System (WPDS) and its components, tokens, patt...

**wp-world-inspire-lab-wi**
- Global Developer capability for World Inspire Lab. Handles Frontend Design , Marketing Page generati...
- Connects to: chrome-devtools

**wordpress-router**
- Use when the user asks about WordPress codebases (plugins, themes, block themes, Gutenberg blocks, W...
- Connects to: wp-project-triage

#### Development (6 skills)

**frontend-patterns**
- Frontend development patterns for React, Next.js, state management, performance optimization, and UI...

**backend-patterns**
- Backend architecture patterns, API design, database optimization, and server-side best practices for...

**cache-components**
- |

**vercel-react-best-practices**
- React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be ...

**coding-standards**
- Universal coding standards, best practices, and patterns for TypeScript, JavaScript, React, and Node...

**tdd-workflow**
- Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven dev...

#### Deployment (5 skills)

**vercel-deployment-guide**
- **Cost:** $0/month

**vps-proxy-setup**
- 自动为您新购买的廉价 VPS 部署 3x-ui + VLESS-Reality，并注入 Clash Verge / ClashMi iOS

**china-global-deployment**
- **Global Performance (Priority):**

**godaddy-dns-manager**
- Manage GoDaddy DNS records via local MCP server using FastMCP.

**cloudflare-dns-manager**
- Manage Cloudflare DNS records via local MCP server. CRUD operations on DNS records across all zones.

#### Utilities (4 skills)

**site-url-extractor**
- Extract all URLs from any website via sitemap parsing + optional crawl fallback

**web-metadata-extractor**
- Extract title, description, Open Graph tags, Twitter Card metadata, and other SEO information from a...

**site-accessibility-judge-China-oversea**
- Analyze if a website is accessible from Global (Overseas) and China locations. Provides IP, GeoIP, a...

**chrome-devtools**
- Control and inspect Chrome browser instances using Chrome DevTools Protocol via MCP.

### Common Cooperation Chains

1. **Design → Code → Deploy**
   - `stitch` → `stitch-react-components` → `vercel-deployment-guide`
   - Design system to production-ready code

2. **WordPress Full Stack**
   - `wp-project-triage` → `wp-block-development` / `wp-plugin-development` → `wp-site-manager`
   - Inspect → Develop → Deploy WordPress projects

3. **Performance Optimization**
   - `site-accessibility-judge-China-oversea` → `wp-performance` / `vercel-react-best-practices` → redeploy
   - Diagnose issues then apply targeted optimizations

### Entry Points

**Where to start in this workflow:**

- **stitch**: Unified router for all Stitch workflows. Use when the user wants to design UI, generate pages, conve...
- **stitch-loop**: Teaches agents to iteratively build websites using Stitch with an autonomous baton-passing loop patt...
- **stitch-enhance-prompt**: Transforms vague UI ideas into polished, Stitch-optimized prompts. Enhances specificity, adds UI/UX ...

### Integration Points

**How this workflow connects to others:**

- **← Writing**: Content management and publishing
- **← 配图**: Visual assets and design systems
- **← 剪辑**: Video content embedding and optimization

---

## Summary

### Statistics

- **Total skills across all workflows:** 103
- **Total workflows:** 4
- **Average skills per workflow:** 25

### Key Insights

1. **Workflows are independent** - Each serves a distinct creative/technical purpose
2. **Workflows are interconnected** - Output from one workflow feeds into others
3. **Phase-based structure** - Each workflow has clear phases (research, create, refine, deploy)
4. **Skill cooperation** - Skills within phases work together seamlessly

### Usage Recommendations

1. **Start at entry points** - Begin with first-phase skills for your workflow
2. **Follow cooperation chains** - Use documented chains for common tasks
3. **Cross-workflow integration** - Leverage integration points to combine workflows
4. **Specialize when needed** - Use specialized skills for specific use cases

