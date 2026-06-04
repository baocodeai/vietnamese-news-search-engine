# Vietnamese News Search Engine

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

### 3. Format commit

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

### 4. Quy định Pull Request

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

### 5. Review code trước khi merge

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

### 6. Quy định merge

- Feature branch chỉ được merge vào `dev` sau khi được approve.
- `dev` chỉ được merge vào `main` khi nhóm thống nhất release/demo.
- Ưu tiên dùng `Squash and merge` cho feature nhỏ để lịch sử commit gọn hơn.
- Sau khi merge thành công, có thể xóa branch feature trên remote.

