# frontend-design 调用提示词

## 使用方法

在 TRAE IDE 的对话中输入以下内容，AI 会自动加载 frontend-design skill 并按此规范生成界面：

---

## 完整提示词（复制以下内容）

```
use the frontend-design skill.

Build a web interface for "公考AI智能学习系统" with the following specifications:

## Design Direction
Natural Wellness + Hand-drawn Aesthetic. The interface should feel like a warm handwritten study notebook — organic, gentle, and陪伴型 (companion-like). Avoid all cold, corporate, or SaaS-template aesthetics.

## Core Context
- **Purpose**: Help civil service exam candidates study without anxiety, using AI to organize questions, generate mind maps, and extract problem-solving methods
- **Audience**: 22-30 year old students and working professionals preparing for civil service exams, who feel stressed and need emotional warmth from their tools
- **Tone**: Warm, gentle, supportive, conversational — like a friend chatting, not a cold tool
- **Differentiation**: Hand-drawn SVG lines, organic border-radius, earth-tone color palette, paper texture background

## Color System (use CSS variables)
```css
:root {
  --background: oklch(0.96 0.015 100);      /* warm cream */
  --background-secondary: oklch(0.94 0.02 90);
  --surface: oklch(1 0 0);                   /* white cards */

  --foreground: oklch(0.3 0.03 80);          /* warm brown text */
  --foreground-secondary: oklch(0.5 0.02 80);
  --muted: oklch(0.75 0.02 100);

  --primary: oklch(0.6 0.12 140);            /* moss green */
  --primary-hover: oklch(0.52 0.13 140);
  --primary-light: oklch(0.85 0.06 140);

  --secondary: oklch(0.7 0.1 45);            /* warm sand */
  --secondary-light: oklch(0.9 0.05 45);

  --accent: oklch(0.65 0.15 25);             /* terracotta */
  --accent-light: oklch(0.85 0.08 25);

  --line-primary: oklch(0.35 0.04 80);       /* warm brown lines */
  --line-secondary: oklch(0.55 0.12 140);    /* moss green lines */

  --radius-hand-drawn: 255px 15px 225px 15px / 15px 225px 15px 255px;
}
```

## Typography
- Display font: "Architects Daughter" (cursive, handwritten feel) — import from Google Fonts
- Body font: "Quicksand" (rounded, friendly sans-serif) — import from Google Fonts
- Use fluid sizing with clamp()
- Line height: 1.6-1.8 for body text
- Max sentence length: 15 Chinese characters for all UI copy

## Copywriting Rules (MUST follow)
- Conversational, like a friend chatting
- Specific with numbers and scenarios
- Humorous, self-deprecating, or provocative is OK
- NO professional jargon, NO Lorem Ipsum, NO passive voice
- Example headline: "慢慢来，比较快" (Take it slow, you'll get there faster)
- Example sub-headline: "AI帮你把厚书读薄，每天只专注搞懂几道题"

## Hand-drawn Line System (CRITICAL visual identity)
1. **Card borders**: Use `border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px;` for organic irregular rounded corners. NOT standard border-radius values.
2. **Divider lines**: Use SVG wave paths, NOT straight lines
3. **Underlines**: Hand-drawn style with irregular shape on CTAs and links
4. **Mind map connections**: SVG bezier curves with slight displacement filter for sketch feel
5. **Decorative elements**: SVG squiggly lines and dots in page corners, low opacity

## Layout
- Asymmetric layout (60/40 split on hero section), NOT centered
- Hero section: Left = headline + CTA, Right = product screenshot in hand-drawn card
- Feature cards: NOT equal height, slightly staggered
- Navigation: Sticky header with hand-drawn wave bottom border

## Animation Rules (NEVER use ease-in-out)
- Card enter (scroll into view): 500ms, cubic-bezier(0.34, 1.56, 0.64, 1) — elastic bounce
- Card hover: 300ms, cubic-bezier(0.34, 1.56, 0.64, 1) — slight lift + border-radius morph
- Button press: 150ms, cubic-bezier(0.4, 0, 0.2, 1) — scale 0.97 then back
- Fade in: 400ms, cubic-bezier(0.25, 0.46, 0.45, 0.94)
- Button hover: 200ms, cubic-bezier(0.25, 0.46, 0.45, 0.94)

## Background
- Base: warm cream color with subtle noise texture overlay (SVG feTurbulence)
- Cards: white with hand-drawn irregular border
- Create atmosphere with texture, NOT solid flat colors

## Anti-Patterns (STRICTLY forbidden)
- NO purple/indigo gradients (#6366F1, #8B5CF6)
- NO Tailwind default color palette
- NO Hero + 3-card center-aligned layout
- NO perfect center alignment
- NO equal-width multi-column
- NO Shadcn/Material UI default components
- NO emoji as icons (use Iconify: https://iconify.design)
- NO linear animations (ease-in-out)
- NO Inter, Roboto, Arial, system fonts
- NO generic AI aesthetics (purple gradients on white, rounded-square icon tiles)

## Components to Build (Home page)
1. Sticky header with logo (hand-drawn style) + navigation + CTA button
2. Hero section: asymmetric 60/40 split with hand-drawn card for product preview
3. Wave SVG divider
4. Three feature cards (not equal height): 题目自动分类 / 导图自动生成 / 方法自动提取
5. Statistics/data section
6. Footer with decorative hand-drawn elements

## Accessibility
- Semantic HTML (header, main, nav, section, article, footer)
- Proper heading hierarchy (h1 → h2 → h3)
- aria-labels on interactive elements
- Color contrast ≥ 4.5:1
- Keyboard navigation support
- focus-visible states with moss green outline
- Support prefers-reduced-motion media query

## Technical Stack
- Vue 3 + TypeScript + `<script setup>` syntax
- Element Plus (deeply customized, NOT default styles)
- CSS custom properties for theming
- SVG for hand-drawn decorative elements
- Google Fonts for typography

Build a complete, production-grade home page that embodies this hand-drawn natural wellness aesthetic. Every element should feel warm, organic, and陪伴型 — like a study companion, not a tool.
```

---

## 快速调用方式

在 TRAE IDE 对话中，你可以根据需要简化提示词：

### 方式一：完整调用（推荐首次使用）
直接粘贴上面的完整提示词，AI 会生成完整首页

### 方式二：分步调用
1. 先说："use the frontend-design skill. 用自然治愈风+手绘感线条设计公考学习系统首页，色调是苔藓绿+暖米白+陶土橙"
2. 等 AI 生成后，再补充具体组件需求，比如："现在画三个功能卡片，用不规则圆角边框，高度不要一样"

### 方式三：局部优化
对已有页面说："use the frontend-design skill. 把这些卡片改成手绘风边框，用 255px 15px 225px 15px / 15px 225px 15px 255px 这种不规则圆角"
