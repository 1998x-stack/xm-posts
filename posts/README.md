# Posts taxonomy

The `posts/<category>/<slug>/index.html` tree is the canonical content source. Categories and second-level topics (`topics: [{slug, title}]`) are defined in `content/categories.json`; each article must specify one registered `category` and primary `topic` in `content/posts.json`. Additional cross-links live in `tags`. This is a logical taxonomy, not an extra directory level. Placeholder category README files deliberately do not represent articles.

Drafts live in their category folders but are excluded until marked `published`. The generated knowledge map at `/topics/` links to `categories/<category>/#topic-<topic>`; zero-post topics are marked planned. Category placeholder README files never publish.

Topic placeholder directory names must match the exact registered topic slug. New content should reuse an existing stable topic whenever scientifically appropriate. The taxonomy contract test checks uniqueness, registered primary topics, placeholder alignment, and published source files.
