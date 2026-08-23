# Skill Overlap Documentation

Generated: document_overlaps.py
Total skill groups analyzed: 4

## Overview

This document identifies and documents functional overlaps between skill groups without proposing consolidation. The goal is to help users understand when to use which skill and how skills complement each other.

## Skill Groups

### WordPress Management

**Skills in group:** 15

#### Skill Descriptions

**wp-cli-expert**
- Expert WordPress management using WP-CLI. Use when the user wants to manage WordPress sites via command line, automate tasks, fix errors (WSOD), bulk update plugins, modify database entries safely, manage multisite networks, configure wp cron jobs, set up wp-cli.yml, or create automation scripts. Triggers include "wp cli", "manage wordpress", "install plugin", "search replace db", "create user", "multisite", "wp cron", "wp-cli.yml", "automation script".

**wp-wpcli-and-ops**
- Use when working with WP-CLI (wp) for WordPress operations: safe search-replace, db export/import, plugin/theme/user/content management, cron, cache flushing, multisite, and scripting/automation with wp-cli.yml.

**wp-site-manager**
- Generic WordPress site management — deploy pages, manage media, execute WP-CLI remotely, site operations, safety protocols. Triggers include "deploy page", "upload media", "wp remote", "site operations", "wp safety", "sitemap sync".

**wp-project-triage**
- Use when you need a deterministic inspection of a WordPress repository (plugin/theme/block theme/WP core/Gutenberg/full site) including tooling/tests/version hints, and a structured JSON report to guide workflows and guardrails.

**wp-block-development**
- Use when developing WordPress (Gutenberg) blocks: block.json metadata, register_block_type(_from_metadata), attributes/serialization, supports, dynamic rendering (render.php/render_callback), deprecations/migrations, viewScript vs viewScriptModule, and @wordpress/scripts/@wordpress/create-block build and test workflows.

**wp-block-themes**
- Use when developing WordPress block themes: theme.json (global settings/styles), templates and template parts, patterns, style variations, and Site Editor troubleshooting (style hierarchy, overrides, caching).

**wp-plugin-development**
- Use when developing WordPress plugins: architecture and hooks, activation/deactivation/uninstall, admin UI and Settings API, data storage, cron/tasks, security (nonces/capabilities/sanitization/escaping), and release packaging.

**wp-rest-api**
- Use when building, extending, or debugging WordPress REST API endpoints/routes: register_rest_route, WP_REST_Controller/controller classes, schema/argument validation, permission_callback/authentication, response shaping, register_rest_field/register_meta, or exposing CPTs/taxonomies via show_in_rest.

**wp-interactivity-api**
- Use when building or debugging WordPress Interactivity API features (data-wp-* directives, @wordpress/interactivity store/state/actions, block viewScriptModule integration, wp_interactivity_*()) including performance, hydration, and directive behavior.

**wp-performance**
- Use when investigating or improving WordPress performance (backend-only agent): profiling and measurement (WP-CLI profile/doctor, Server-Timing, Query Monitor via REST headers), database/query optimization, autoloaded options, object caching, cron, HTTP API calls, and safe verification.

**wp-phpstan**
- Use when configuring, running, or fixing PHPStan static analysis in WordPress projects (plugins/themes/sites): phpstan.neon setup, baselines, WordPress-specific typing, and handling third-party plugin classes.

**wp-playground**
- Use for WordPress Playground workflows: fast disposable WP instances in the browser or locally via @wp-playground/cli (server, run-blueprint, build-snapshot), auto-mounting plugins/themes, switching WP/PHP versions, blueprints, and debugging (Xdebug).

**wpds**
- Use when building UIs leveraging the WordPress Design System (WPDS) and its components, tokens, patterns, etc.

**wp-world-inspire-lab-wi**
- Global Developer capability for World Inspire Lab. Handles Frontend Design , Marketing Page generation, and Responsiveness updates via WordPress API.

**wordpress-router**
- Use when the user asks about WordPress codebases (plugins, themes, block themes, Gutenberg blocks, WP core checkouts) and you need to quickly classify the repo and route to the correct workflow/skill (blocks, theme.json, REST API, WP-CLI, performance, security, testing, release packaging).

#### Capability Matrix

| Skill | analysis | building | configuration | creation | debugging | deployment | design | development | enhancement | generation | management | testing |
|-------|---|---|---|---|---|---|---|---|---|---|---|---|
| wp-cli-expert |  |  | ✓ | ✓ |  |  |  | ✓ |  | ✓ | ✓ | ✓ |
| wp-wpcli-and-ops |  | ✓ |  |  | ✓ |  |  |  |  |  | ✓ | ✓ |
| wp-site-manager |  | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ |  |
| wp-project-triage |  | ✓ |  |  | ✓ |  |  |  |  |  |  | ✓ |
| wp-block-development |  | ✓ |  | ✓ | ✓ |  |  | ✓ |  |  |  | ✓ |
| wp-block-themes |  | ✓ |  | ✓ | ✓ |  |  | ✓ |  |  |  | ✓ |
| wp-plugin-development |  | ✓ |  |  | ✓ |  |  | ✓ |  |  |  | ✓ |
| wp-rest-api |  | ✓ |  | ✓ | ✓ |  |  |  |  |  | ✓ | ✓ |
| wp-interactivity-api |  | ✓ |  | ✓ | ✓ |  |  |  | ✓ |  |  | ✓ |
| wp-performance |  |  |  |  | ✓ |  |  |  |  | ✓ |  | ✓ |
| wp-phpstan | ✓ | ✓ |  |  | ✓ |  |  |  |  | ✓ | ✓ | ✓ |
| wp-playground |  | ✓ |  |  | ✓ |  |  |  |  |  |  | ✓ |
| wpds |  | ✓ | ✓ |  |  |  | ✓ |  |  |  |  |  |
| wp-world-inspire-lab-wi |  | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  |  | ✓ |  |
| wordpress-router |  | ✓ |  | ✓ | ✓ |  |  |  |  |  | ✓ | ✓ |

#### Overlap Analysis

**wp-project-triage** ↔ **wp-playground**: 100% overlap
- Common capabilities: building, debugging, testing

**wp-block-development** ↔ **wp-block-themes**: 100% overlap
- Common capabilities: building, creation, debugging, development, testing

**wp-rest-api** ↔ **wordpress-router**: 100% overlap
- Common capabilities: building, creation, debugging, management, testing

**wp-site-manager** ↔ **wp-world-inspire-lab-wi**: 88% overlap
- Common capabilities: building, creation, debugging, deployment, design, development, management

**wp-wpcli-and-ops** ↔ **wp-rest-api**: 80% overlap
- Common capabilities: building, debugging, management, testing

**wp-wpcli-and-ops** ↔ **wordpress-router**: 80% overlap
- Common capabilities: building, debugging, management, testing

**wp-block-development** ↔ **wp-plugin-development**: 80% overlap
- Common capabilities: building, debugging, development, testing

**wp-block-themes** ↔ **wp-plugin-development**: 80% overlap
- Common capabilities: building, debugging, development, testing

**wp-wpcli-and-ops** ↔ **wp-project-triage**: 75% overlap
- Common capabilities: building, debugging, testing

**wp-wpcli-and-ops** ↔ **wp-playground**: 75% overlap
- Common capabilities: building, debugging, testing

**wp-project-triage** ↔ **wp-plugin-development**: 75% overlap
- Common capabilities: building, debugging, testing

**wp-plugin-development** ↔ **wp-playground**: 75% overlap
- Common capabilities: building, debugging, testing

**wp-wpcli-and-ops** ↔ **wp-phpstan**: 67% overlap
- Common capabilities: building, debugging, management, testing

**wp-block-development** ↔ **wp-rest-api**: 67% overlap
- Common capabilities: building, creation, debugging, testing

**wp-block-development** ↔ **wp-interactivity-api**: 67% overlap
- Common capabilities: building, creation, debugging, testing

**wp-block-development** ↔ **wordpress-router**: 67% overlap
- Common capabilities: building, creation, debugging, testing

**wp-block-themes** ↔ **wp-rest-api**: 67% overlap
- Common capabilities: building, creation, debugging, testing

**wp-block-themes** ↔ **wp-interactivity-api**: 67% overlap
- Common capabilities: building, creation, debugging, testing

**wp-block-themes** ↔ **wordpress-router**: 67% overlap
- Common capabilities: building, creation, debugging, testing

**wp-rest-api** ↔ **wp-interactivity-api**: 67% overlap
- Common capabilities: building, creation, debugging, testing

**wp-interactivity-api** ↔ **wordpress-router**: 67% overlap
- Common capabilities: building, creation, debugging, testing

**wp-wpcli-and-ops** ↔ **wp-plugin-development**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-project-triage** ↔ **wp-block-development**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-project-triage** ↔ **wp-block-themes**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-project-triage** ↔ **wp-rest-api**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-project-triage** ↔ **wp-interactivity-api**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-project-triage** ↔ **wordpress-router**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-block-development** ↔ **wp-playground**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-block-themes** ↔ **wp-playground**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-rest-api** ↔ **wp-playground**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-interactivity-api** ↔ **wp-playground**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-playground** ↔ **wordpress-router**: 60% overlap
- Common capabilities: building, debugging, testing

**wp-rest-api** ↔ **wp-phpstan**: 57% overlap
- Common capabilities: building, debugging, management, testing

**wp-phpstan** ↔ **wordpress-router**: 57% overlap
- Common capabilities: building, debugging, management, testing

**wp-wpcli-and-ops** ↔ **wp-block-development**: 50% overlap
- Common capabilities: building, debugging, testing

**wp-wpcli-and-ops** ↔ **wp-block-themes**: 50% overlap
- Common capabilities: building, debugging, testing

**wp-wpcli-and-ops** ↔ **wp-interactivity-api**: 50% overlap
- Common capabilities: building, debugging, testing

**wp-project-triage** ↔ **wp-performance**: 50% overlap
- Common capabilities: debugging, testing

**wp-project-triage** ↔ **wp-phpstan**: 50% overlap
- Common capabilities: building, debugging, testing

**wp-block-development** ↔ **wp-world-inspire-lab-wi**: 50% overlap
- Common capabilities: building, creation, debugging, development

**wp-block-themes** ↔ **wp-world-inspire-lab-wi**: 50% overlap
- Common capabilities: building, creation, debugging, development

**wp-plugin-development** ↔ **wp-rest-api**: 50% overlap
- Common capabilities: building, debugging, testing

**wp-plugin-development** ↔ **wp-interactivity-api**: 50% overlap
- Common capabilities: building, debugging, testing

**wp-plugin-development** ↔ **wordpress-router**: 50% overlap
- Common capabilities: building, debugging, testing

**wp-rest-api** ↔ **wp-world-inspire-lab-wi**: 50% overlap
- Common capabilities: building, creation, debugging, management

**wp-performance** ↔ **wp-phpstan**: 50% overlap
- Common capabilities: debugging, generation, testing

**wp-performance** ↔ **wp-playground**: 50% overlap
- Common capabilities: debugging, testing

**wp-phpstan** ↔ **wp-playground**: 50% overlap
- Common capabilities: building, debugging, testing

**wp-world-inspire-lab-wi** ↔ **wordpress-router**: 50% overlap
- Common capabilities: building, creation, debugging, management

**wp-site-manager** ↔ **wp-block-development**: 44% overlap
- Common capabilities: building, creation, debugging, development

**wp-site-manager** ↔ **wp-block-themes**: 44% overlap
- Common capabilities: building, creation, debugging, development

**wp-site-manager** ↔ **wp-rest-api**: 44% overlap
- Common capabilities: building, creation, debugging, management

**wp-site-manager** ↔ **wp-interactivity-api**: 44% overlap
- Common capabilities: building, creation, debugging, enhancement

**wp-site-manager** ↔ **wordpress-router**: 44% overlap
- Common capabilities: building, creation, debugging, management

**wp-plugin-development** ↔ **wp-phpstan**: 43% overlap
- Common capabilities: building, debugging, testing

**wp-wpcli-and-ops** ↔ **wp-performance**: 40% overlap
- Common capabilities: debugging, testing

**wp-plugin-development** ↔ **wp-performance**: 40% overlap
- Common capabilities: debugging, testing

**wp-cli-expert** ↔ **wp-block-development**: 38% overlap
- Common capabilities: creation, development, testing

**wp-cli-expert** ↔ **wp-block-themes**: 38% overlap
- Common capabilities: creation, development, testing

**wp-cli-expert** ↔ **wp-rest-api**: 38% overlap
- Common capabilities: creation, management, testing

**wp-cli-expert** ↔ **wordpress-router**: 38% overlap
- Common capabilities: creation, management, testing

**wp-wpcli-and-ops** ↔ **wp-world-inspire-lab-wi**: 38% overlap
- Common capabilities: building, debugging, management

**wp-block-development** ↔ **wp-phpstan**: 38% overlap
- Common capabilities: building, debugging, testing

**wp-block-themes** ↔ **wp-phpstan**: 38% overlap
- Common capabilities: building, debugging, testing

**wp-plugin-development** ↔ **wp-world-inspire-lab-wi**: 38% overlap
- Common capabilities: building, debugging, development

**wp-interactivity-api** ↔ **wp-phpstan**: 38% overlap
- Common capabilities: building, debugging, testing

**wp-cli-expert** ↔ **wp-phpstan**: 33% overlap
- Common capabilities: generation, management, testing

**wp-wpcli-and-ops** ↔ **wp-site-manager**: 33% overlap
- Common capabilities: building, debugging, management

**wp-site-manager** ↔ **wp-plugin-development**: 33% overlap
- Common capabilities: building, debugging, development

**wp-block-development** ↔ **wp-performance**: 33% overlap
- Common capabilities: debugging, testing

**wp-block-themes** ↔ **wp-performance**: 33% overlap
- Common capabilities: debugging, testing

**wp-rest-api** ↔ **wp-performance**: 33% overlap
- Common capabilities: debugging, testing

**wp-interactivity-api** ↔ **wp-performance**: 33% overlap
- Common capabilities: debugging, testing

**wp-interactivity-api** ↔ **wp-world-inspire-lab-wi**: 33% overlap
- Common capabilities: building, creation, debugging

**wp-performance** ↔ **wordpress-router**: 33% overlap
- Common capabilities: debugging, testing

#### When to Use Which Skill

**Decision Guidelines:**

- **wp-cli-expert / wp-wpcli-and-ops**: Direct WP-CLI command execution
- **wp-site-manager**: Full site deployment and management
- **wp-project-triage**: Diagnostic and inspection workflows
- **wp-block-development / wp-block-themes**: Gutenberg block/theme development
- **wp-plugin-development**: Plugin architecture and development
- **wp-rest-api**: REST API extension and debugging
- **wp-performance**: Performance optimization and profiling
- **wp-playground**: Fast prototyping without server setup

---

### E-Commerce Landing Pages

**Skills in group:** 2

#### Skill Descriptions

**ecommerce-landing-page**
- 电商详情页(Landing Page/Detail Page)设计专家。从产品分析、卖点提炼、文案排版规划到最终的高清视觉图生成。支持国内/国外电商多渠道适配。

**ecommerce-lp-generator**
- 专业的电商详情页(Landing Page)生成技能,采用网格生成技术确保一致性和效率。输入产品图片 -> 输出一系列切片的高清详情页设计图。

#### Capability Matrix

| Skill | building | creation | debugging | design | generation | testing | upscaling |
|-------|---|---|---|---|---|---|---|
| ecommerce-landing-page |  | ✓ | ✓ | ✓ | ✓ |  | ✓ |
| ecommerce-lp-generator | ✓ |  |  | ✓ | ✓ | ✓ |  |

#### Overlap Analysis

No significant overlaps detected (>30% capability overlap).

#### When to Use Which Skill

**Decision Guidelines:**

- **ecommerce-landing-page**: Comprehensive landing page design with product analysis
- **ecommerce-lp-generator**: Grid-based generation for consistency and efficiency

---

### Image Enhancement

**Skills in group:** 3

#### Skill Descriptions

**image-enhancer**
- Improves the quality of images, especially screenshots, by enhancing resolution, sharpness, and clarity. Perfect for preparing images for presentations, documentation, or social media posts.

**repair-old-photos**
- Restore and repair old, damaged, or low-quality photos. Use when the user provides an old photo and asks to "fix", "repair", or "restore" it while keeping the content (faces, clothes, poses) 100% identical.

**topaz-photo-ai-upscaler**
- Professional AI-powered image upscaling using Topaz Photo AI CLI. Better quality than Upscayl for camera photos, with intelligent autopilot and manual controls.

#### Capability Matrix

| Skill | analysis | enhancement | generation | optimization | restoration | testing | upscaling |
|-------|---|---|---|---|---|---|---|
| image-enhancer | ✓ | ✓ |  | ✓ |  |  | ✓ |
| repair-old-photos |  |  | ✓ |  | ✓ | ✓ |  |
| topaz-photo-ai-upscaler | ✓ | ✓ |  | ✓ |  |  | ✓ |

#### Overlap Analysis

**image-enhancer** ↔ **topaz-photo-ai-upscaler**: 100% overlap
- Common capabilities: analysis, enhancement, optimization, upscaling

#### When to Use Which Skill

**Decision Guidelines:**

- **image-enhancer**: General image quality improvement
- **repair-old-photos**: Specialized restoration for damaged/old photos
- **topaz-photo-ai-upscaler**: Professional AI upscaling using Topaz Photo AI

---

### Life Coaching

**Skills in group:** 3

#### Skill Descriptions

**elon-musk-life-coach**
- Life coaching from Elon Musk's perspective. Use when the user asks for life advice, career guidance, problem-solving strategies, productivity tips, or wants to think through challenges using first principles. Mimics Elon's direct communication style and his philosophies on work, innovation, simplicity, and execution. Triggered by phrases like "what would Elon do", "life coach", "career advice", "first principles", "how to approach [problem]", or mentions of productivity/effectiveness.

**lifestyle-aesthetic-designer**
- Proactive coaching and day-design based on the "Life Aesthetic" philosophy (Inner Glow, 60% Energy Rule, Dance Linkage).

**consultant-friend**
- A strategic advisor who thinks like a McKinsey partner (MECE, structured) but speaks like a close friend (natural, candid, jargon-free). Use when the user needs deep problem analysis or strategic advice without the corporate stiff upper lip.

#### Capability Matrix

| Skill | building | coaching | creation | design | optimization | testing |
|-------|---|---|---|---|---|---|
| elon-musk-life-coach | ✓ | ✓ | ✓ |  |  |  |
| lifestyle-aesthetic-designer |  | ✓ | ✓ | ✓ |  |  |
| consultant-friend |  |  |  |  | ✓ | ✓ |

#### Overlap Analysis

**elon-musk-life-coach** ↔ **lifestyle-aesthetic-designer**: 50% overlap
- Common capabilities: coaching, creation

#### When to Use Which Skill

**Decision Guidelines:**

- **elon-musk-life-coach**: Elon Musk's perspective and principles
- **lifestyle-aesthetic-designer**: Proactive day design and aesthetic coaching
- **consultant-friend**: Strategic McKinsey-style business advisory

---

## Summary

### Key Findings

- **Total skills analyzed:** 23
- **Skill groups:** 4
- **Largest group:** WordPress Management (15 skills)
- **Overlap type:** Complementary (skills serve different aspects of same domain)

### Recommendations

1. **No consolidation needed** - Skills serve distinct use cases within their domains
2. **Document workflows** - Show how skills work together in multi-step processes
3. **Improve discovery** - Help users find the right skill for their specific need
4. **Cross-reference** - Add "See also" sections in SKILL.md files

