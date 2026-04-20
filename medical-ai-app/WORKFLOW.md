# Git Workflow Template (MedAI Assist)

Template ngắn để track task rõ ràng và quay lại version nhanh.

## 1) Quy ước branch

- `main`: nhánh ổn định, chỉ nhận code đã review.
- `feature/<scope>-<short-name>`: tính năng mới.
- `fix/<scope>-<short-name>`: sửa bug.
- `refactor/<scope>-<short-name>`: cải tổ code không đổi behavior.
- `chore/<short-name>`: việc kỹ thuật (deps, config, scripts).

Ví dụ:

- `feature/dashboard-module-cards`
- `fix/mri-overlay-visibility`
- `chore/backend-ml-deps`

## 2) Quy ước commit message

Format:

`<type>(<scope>): <short summary>`

Types đề xuất:

- `feat`: thêm chức năng
- `fix`: sửa bug
- `refactor`: đổi cấu trúc code
- `docs`: tài liệu
- `chore`: việc phụ trợ
- `style`: chỉnh UI/CSS không đổi logic
- `test`: thêm/chỉnh test

Ví dụ:

- `feat(dashboard): replace module cards with real medical images`
- `fix(brain-mri): add required CBIM dependencies`
- `style(analysis): add MRI class legend in result panel`
- `docs(workflow): add git branch and tag conventions`

## 3) Quy ước tag để quay lại version

Tag theo mốc release hoặc snapshot quan trọng:

- Release: `v<major>.<minor>.<patch>` (ví dụ: `v1.2.0`)
- Snapshot UI/ML nội bộ: `<area>-<yyyy-mm-dd>-r<index>`
  - ví dụ: `ui-2026-04-20-r1`
  - ví dụ: `mri-2026-04-20-r2`

Tạo tag:

```bash
git tag -a v1.2.0 -m "Release v1.2.0: dashboard + MRI legend"
git tag -a ui-2026-04-20-r1 -m "UI snapshot before filter refactor"
```

Push tag:

```bash
git push origin v1.2.0
git push origin --tags
```

## 4) Vòng làm việc ngắn cho mỗi task

1. Cập nhật `main`:

   ```bash
   git checkout main
   git pull
   ```

2. Tạo nhánh task:

   ```bash
   git checkout -b feature/dashboard-module-cards
   ```

3. Commit theo lát cắt nhỏ:

   ```bash
   git add .
   git commit -m "style(dashboard): update module card image layout"
   ```

4. Push và tạo PR:

   ```bash
   git push -u origin feature/dashboard-module-cards
   ```

5. Sau merge, gắn tag nếu là mốc quan trọng.

## 5) Cách quay về version cũ an toàn

- Xem lịch sử nhanh:

  ```bash
  git log --oneline --graph --decorate
  ```

- Tạo nhánh từ commit cũ để kiểm tra:

  ```bash
  git checkout -b hotfix/from-old <commit-hash>
  ```

- Khôi phục 1 file về commit cũ:

  ```bash
  git restore --source <commit-hash> frontend/src/pages/DashboardPage.tsx
  ```

- Hoàn tác 1 commit đã đẩy (không phá lịch sử):

  ```bash
  git revert <commit-hash>
  ```

## 6) Checklist trước khi merge

- Build frontend pass
- API backend chạy ổn
- UI không vỡ layout desktop
- Commit message đúng format
- PR title bám theo commit style

## 7) Cheatsheet 30 giây (10 lệnh dùng hằng ngày)

```bash
# 1) Xem trạng thái thay đổi
git status

# 2) Xem lịch sử gọn
git log --oneline --graph --decorate -n 15

# 3) Cập nhật main mới nhất
git checkout main && git pull

# 4) Tạo nhánh mới từ main
git checkout -b feature/<scope>-<name>

# 5) Thêm toàn bộ thay đổi
git add .

# 6) Commit theo format chuẩn
git commit -m "feat(scope): short summary"

# 7) Push nhánh lần đầu
git push -u origin HEAD

# 8) Gắn tag snapshot/release
git tag -a <tag-name> -m "tag note"

# 9) Khôi phục 1 file từ commit cũ
git restore --source <commit-hash> <path/to/file>

# 10) Hoàn tác commit an toàn (không rewrite history)
git revert <commit-hash>
```

## 8) Quay về version cũ có sửa và chạy được không?

Có, chạy được. Nhưng để ổn định cần theo đúng thứ tự này:

1. Checkout commit/tag cũ trên nhánh mới:

   ```bash
   git checkout -b test/old-version <commit-or-tag>
   ```

2. Cài lại dependency theo đúng version của commit đó:

   ```bash
   # backend
   cd backend
   .venv\Scripts\activate
   pip install -r requirements.txt

   # frontend
   cd ../frontend
   npm install
   ```

3. Chạy lại service:

   ```bash
   # backend
   cd ../backend
   uvicorn app.main:app --reload --port 8000

   # frontend
   cd ../frontend
   npm run dev
   ```

4. Nếu commit cũ đổi schema DB thì tạo lại DB sạch:

   ```bash
   cd ../backend
   python init_db.py
   ```

Lưu ý thực tế:

- Code quay về cũ nhưng môi trường không quay về tự động; lỗi thường nằm ở `requirements.txt`, `package-lock.json`, hoặc DB schema.
- Nếu muốn quay lại tạm thời để test mà không ảnh hưởng code hiện tại, luôn tạo nhánh mới từ commit/tag cũ như bước 1.
