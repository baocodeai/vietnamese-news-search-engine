# Vietnamese News Search Engine

## Demo Operation Guide

Install backend dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-semantic.txt
```

Build keyword index:

```bash
conda run -n searchengine python scripts/build_lexical_index.py --limit 1000
```

Build semantic E5 + FAISS index:

```bash
conda run -n searchengine python scripts/build_semantic_index.py --limit 1000
```

Search semantic artifact from CLI:

```bash
conda run -n searchengine python scripts/search_semantic_index.py --query "cuop tiem vang" --top-k 5
```

Run backend:

```bash
conda run -n searchengine uvicorn backend.app.main:app --reload
```

Run frontend:

```bash
cd frontend
npm install
npm run dev
```

The search API accepts `mode=keyword|semantic|hybrid`. The UI exposes the same modes in the search bar. `keyword` is the default and does not require semantic dependencies or artifacts. `semantic` and `hybrid` require the semantic artifacts in `data/embeddings/e5_base`.

Dự án xây dựng search engine cho báo tiếng Việt của nhóm 5 thành viên: Bảo, Tài, Vinh, Duy, Phúc.

## Quy định Git Workflow

### 1. Branch chính

- `main`: branch ổn định nhất, chỉ chứa code đã được review, test và sẵn sàng release/demo.
- `dev`: branch tích hợp chính trong quá trình phát triển. Tất cả feature sau khi hoàn thành sẽ merge vào `dev` trước.
- Không commit trực tiếp lên `main` hoặc `dev`.
- Chỉ merge từ `dev` vào `main` khi nhóm thống nhất đã đủ ổn định để release/demo.

### 2. Branch theo feature

Mỗi task hoặc feature phải được làm trên branch riêng, tách ra từ `dev`.

Format đặt tên branch:

```text
feature/<ten-ngan-gon>
fix/<ten-loi>
docs/<noi-dung-tai-lieu>
refactor/<noi-dung-refactor>
```

Ví dụ:

```text
feature/crawler-vnexpress
feature/search-api
fix/tokenizer-error
docs/git-workflow
refactor-ranking-service
```

Quy trình làm feature:

1. Cập nhật `dev` mới nhất.
2. Tạo branch mới từ `dev`.
3. Code và commit theo đúng format.
4. Push branch lên remote.
5. Tạo Pull Request vào `dev`.
6. Chờ review và sửa comment nếu có.
7. Merge sau khi PR được approve.

### 3. Quy trình thao tác Git

#### 3.1. Lấy code mới nhất trước khi làm việc

Trước khi bắt đầu làm task, luôn cập nhật branch `dev` mới nhất:

```bash
git checkout dev
git fetch origin
git pull origin dev
```

Ý nghĩa:

- `git checkout dev`: chuyển sang branch `dev`.
- `git fetch origin`: lấy thông tin branch mới nhất từ remote nhưng chưa merge vào code local.
- `git pull origin dev`: tải và merge code mới nhất từ remote `dev` vào local `dev`.

#### 3.2. Tạo branch mới cho task

Sau khi đã cập nhật `dev`, tạo branch riêng cho feature hoặc bug fix:

```bash
git checkout -b feature/<ten-ngan-gon>
```

Ví dụ:

```bash
git checkout -b feature/search-api
```

#### 3.3. Kiểm tra trạng thái file

Trong quá trình code, thường xuyên kiểm tra file đã thay đổi:

```bash
git status
```

Lệnh này giúp biết:

- File nào đã sửa.
- File nào mới được tạo.
- File nào đã được đưa vào staging area.
- File nào chưa được commit.

#### 3.4. Thêm file vào staging area

Thêm toàn bộ thay đổi:

```bash
git add .
```

Hoặc chỉ thêm file cụ thể:

```bash
git add README.md
git add backend/app/main.py
```

Không nên `git add .` nếu trong project đang có file tạm, log, cache hoặc dữ liệu không nên commit. Khi không chắc chắn, dùng `git status` trước.

#### 3.5. Commit thay đổi

Commit theo đúng format quy định:

```bash
git commit -m "feat: add search API"
```

Ví dụ khác:

```bash
git commit -m "fix: handle empty search query"
git commit -m "docs: update git workflow"
```

#### 3.6. Push branch lên remote

Lần đầu push branch mới:

```bash
git push -u origin feature/<ten-ngan-gon>
```

Ví dụ:

```bash
git push -u origin feature/search-api
```

Những lần sau trên cùng branch chỉ cần:

```bash
git push
```

#### 3.7. Cập nhật branch feature khi `dev` có code mới

Nếu `dev` đã có thay đổi mới trong lúc đang làm feature, cập nhật branch của mình:

```bash
git checkout dev
git fetch origin
git pull origin dev
git checkout feature/<ten-ngan-gon>
git merge dev
```

Nếu có conflict, người làm branch phải tự xử lý conflict, test lại, commit và push lại.

#### 3.8. Tạo Pull Request

Sau khi đã push branch lên remote:

1. Mở GitHub/GitLab.
2. Tạo Pull Request từ branch feature vào `dev`.
3. Điền mô tả PR theo template.
4. Chờ thành viên khác review.
5. Sửa comment nếu có.
6. Merge sau khi PR được approve và test/build pass.

#### 3.9. Sau khi PR đã merge

Sau khi feature branch đã được merge vào `dev`, cập nhật lại local:

```bash
git checkout dev
git pull origin dev
```

Sau đó có thể xóa branch local nếu không dùng nữa:

```bash
git branch -d feature/<ten-ngan-gon>
```

### 4. Format commit

Commit message dùng format:

```text
<type>: <mo-ta-ngan-gon>
```

Các `type` được dùng:

- `feat`: thêm tính năng mới.
- `fix`: sửa lỗi.
- `docs`: cập nhật tài liệu.
- `refactor`: chỉnh sửa code nhưng không đổi behavior.
- `test`: thêm hoặc sửa test.
- `chore`: việc phụ trợ như cấu hình, dependency, format.

Ví dụ:

```text
feat: add Vietnamese text tokenizer
fix: handle empty query in search API
docs: add git workflow rules
refactor: split crawler service
test: add ranking unit tests
chore: update docker config
```

Yêu cầu khi commit:

- Commit nhỏ, tập trung vào một mục đích rõ ràng.
- Không commit file tạm, log, cache, dữ liệu lớn hoặc thông tin nhạy cảm.
- Không gộp nhiều thay đổi không liên quan vào một commit.

### 5. Quy định Pull Request

Mỗi Pull Request phải:

- Merge vào `dev`, trừ PR release từ `dev` vào `main`.
- Có tiêu đề rõ ràng, mô tả đúng nội dung thay đổi.
- Ghi rõ task/feature đã làm, cách test, và ảnh chụp màn hình nếu có thay đổi UI.
- Không chứa thay đổi ngoài phạm vi task.
- Không tự merge PR của mình nếu chưa có review.

Template mô tả PR:

```markdown
## Nội dung thay đổi

- ...

## Cách kiểm tra

- ...

## Ghi chú

- ...
```

### 6. Review code trước khi merge

Trước khi merge, PR cần ít nhất 1 thành viên khác review và approve.

Reviewer cần kiểm tra:

- Code có đúng yêu cầu task không.
- Logic có rõ ràng, dễ bảo trì không.
- Có lỗi tiềm ẩn, case biên hoặc vấn đề performance không.
- Có ảnh hưởng tới module khác không.
- Có cần thêm hoặc cập nhật test không.
- Có vi phạm format, convention hoặc cấu trúc dự án không.

Người tạo PR cần:

- Phản hồi tất cả comment review.
- Sửa lỗi hoặc giải thích rõ nếu không sửa.
- Cập nhật branch nếu `dev` đã thay đổi nhiều.
- Đảm bảo build/test pass trước khi merge.

### 7. Quy định merge

- Feature branch chỉ được merge vào `dev` sau khi được approve.
- `dev` chỉ được merge vào `main` khi nhóm thống nhất release/demo.
- Ưu tiên dùng `Squash and merge` cho feature nhỏ để lịch sử commit gọn hơn.
- Sau khi merge thành công, có thể xóa branch feature trên remote.
