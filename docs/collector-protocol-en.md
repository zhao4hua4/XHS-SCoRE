# XHS-SCoRE Collector Protocol — English Reconstruction

## Status and purpose

This document is a curated English reconstruction of the Chinese video instructions provided to XHS-SCoRE collectors. It preserves the original collection logic and workflow while removing duplicated speech-recognition output and correcting obvious transcription errors. It is documentation of the original protocol, not a new protocol.

The collection target was the collector's **immediate first-person response** while browsing Xiaohongshu. Collectors were not asked to infer author intention or assign a reader-independent semantic property to a post.

## Source platform and text-only requirement

1. Collect every item from **Xiaohongshu**.
2. Record only posts whose relevant meaning can be understood from the **text alone**.
3. Avoid posts for which the comparison response depends on an image, video, layout, or other unavailable multimodal context.
4. Copy the post text faithfully into the provided spreadsheet.

## Collection categories

Collectors used three response categories.

### NEUTRAL / no clear comparison

Collect a post when reading it does not lead you to compare your situation with the poster's situation, or when no clear reader–poster comparison is elicited.

The instruction video used a weather-information post as a simple example: after reading it, the collector had no wish or basis to compare themselves with the poster.

### UPWARD comparison

Collect a post when the poster appears **better off than you** in a way that elicits comparison.

The instruction video used a high-quality travel/lifestyle post as an example. A reader might compare the poster's rich travel experience with their own more limited experience and feel relatively disadvantaged, envious, or inadequate.

### DOWNWARD comparison

Collect a post when the poster appears **worse off than you** in a way that elicits comparison.

The instruction video used a post about an adult becoming distressed because of family-of-origin conflict as an example. A reader might compare family circumstances and feel relatively fortunate or better situated.

## Personal-response principle

Comparison elicitation is reader-dependent. The same post may elicit comparison for one reader and no comparison for another. Collectors were therefore instructed to rely on **their own immediate feeling and response**, rather than guessing how most people would respond or trying to recover the poster's intention.

## Seven-day collection schedule

Collection continued for seven consecutive days. Each day, every collector identified:

- 10 NEUTRAL / no-clear-comparison posts;
- 10 UPWARD-comparison posts; and
- 10 DOWNWARD-comparison posts.

The target was therefore **30 posts per day** and **210 posts per collector** in total: 70 NEUTRAL, 70 UPWARD, and 70 DOWNWARD.

## Spreadsheet workflow

Collectors received structured spreadsheet templates, separated by day and category.

For each post, the template requested:

- post text;
- Xiaohongshu link;
- poster username;
- poster gender, when visible;
- posting location, when visible;
- poster age, when visible; and
- poster occupation, when visible.

Metadata fields that were not visible on Xiaohongshu could be left blank. Example rows supplied in the template were to be deleted before submission.

## Capturing links

Collectors were encouraged to use the Xiaohongshu web interface. The instruction video demonstrated using the platform's share/link control to copy the post URL into the spreadsheet.

## Submission and data handling

Collectors submitted completed spreadsheets through the designated project channel after following the daily schedule. Raw collected platform posts and potentially identifying metadata are **not redistributed in this repository**. The public release contains policy-compliant generated materials, documentation, scripts/configurations, predictions, and aggregate diagnostics.

## Operational summary

For each candidate post, ask:

1. Is it from Xiaohongshu?
2. Is the relevant meaning recoverable from text alone?
3. What is my immediate first-person response?
   - no clear reader–poster comparison → **NEUTRAL**;
   - poster appears better off than me → **UPWARD**;
   - poster appears worse off than me → **DOWNWARD**.
4. Have I recorded the text and link, plus only the metadata visible on the platform?
5. Does the item contribute to today's target of 10 posts in this category?

## Relationship to the benchmark

This protocol operationalizes XHS-SCoRE as a **reader-group-conditioned elicitation task**. The collected response is the target label. Subsequent agreement, stability, and ambiguity analyses calibrate that target; they do not replace the original collector's immediate response with a universal consensus label.
