# copyast

`copyast` là CLI tool dùng để export source code dạng text vào một file bundle duy nhất, hỗ trợ:

- export toàn bộ source từ một hoặc nhiều root directory
- import / update file hoặc directory vào bundle
- delete block khỏi bundle
- scan-delete theo substring
- sync bundle theo thay đổi Git
- merge thêm nội dung vào bundle hiện có bằng `--append`

---

## 1. Yêu cầu

- Python 3.11 trở lên

Project hiện khai báo trong `pyproject.toml`:

```toml
requires-python = ">=3.11"
```

---

## 2. Cài đặt

### 2.1 Cách khuyên dùng: editable install

Tại thư mục root của project:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
```

Sau khi cài xong, có thể chạy:

```bash
copyast --help
```

Project đã khai báo console script:

```toml
[project.scripts]
copyast = "app.main:main"
```

nên sau `pip install -e .` không cần gọi `python -m ...` nữa.

---

### 2.2 Chạy nhanh khi chưa cài editable

Project đang dùng `src` layout, nên nếu chưa chạy `pip install -e .`, có thể chạy:

```bash
PYTHONPATH=src python -m app.main --help
```

hoặc:

```bash
cd src
python -m app.main --help
```

---

## 3. Cấu trúc bundle

Mỗi file trong bundle được lưu theo block:

```txt
 === FILE: path/to/file.py ===
<file content>

 === FILE: another/file.txt ===
<file content>
```

Nếu export từ **nhiều root directory**, path trong bundle sẽ được prefix bằng alias để tránh trùng tên file:

```txt
 === FILE: app/src/main.py ===
...
 === FILE: ci/.github/workflows/ci.yml ===
...
```

---

## 4. Các command hiện có

* `export`
* `import`
* `bulk-import`
* `delete`
* `bulk-delete`
* `scan-delete`
* `sync-git`

---

## 5. Quy ước root directory

Các command có hỗ trợ root dùng cờ:

```bash
--root-dir
```

### 5.1 Một root

```bash
copyast export \
  --root-dir . \
  --export ./copyast-output.txt
```

### 5.2 Nhiều root

Có thể lặp lại `--root-dir` nhiều lần:

```bash
copyast export \
  --root-dir ../repo-a \
  --root-dir ../repo-b \
  --export ./copyast-output.txt
```

### 5.3 Nhiều root kèm alias

Nên dùng alias để path trong bundle rõ ràng hơn:

```bash
copyast export \
  --root-dir app=../auto-asset-tool \
  --root-dir ci=../gitlab-ci \
  --export ./copyast-output.txt
```

Khi đó file trong bundle sẽ có dạng:

* `app/src/app/main.py`
* `ci/.github/workflows/ci.yml`

> Lưu ý: alias phải là duy nhất. Nếu bị trùng alias, chương trình sẽ báo lỗi.

---

## 6. Cách dùng chi tiết

## 6.1 Export toàn bộ source vào bundle

Ví dụ export từ một root:

```bash
copyast export \
  --root-dir . \
  --export ./copyast-output.txt \
  --ignore '.idea/' \
  --ignore '.git/' \
  --ignore '.env' \
  --ignore-file '.copyastignore.example'
```

### Ý nghĩa

* `--root-dir`: thư mục project gốc, có thể truyền nhiều lần
* `--export`: file bundle đầu ra
* `--ignore`: thêm pattern ignore bằng tay
* `--ignore-file`: file ignore tương đối theo từng root
* `--append`: merge vào bundle cũ thay vì ghi đè toàn bộ

### Cách hoạt động

Khi export, `copyast` sẽ:

* duyệt toàn bộ file trong từng `root-dir`
* bỏ qua chính file export
* bỏ qua file match ignore rule
* bỏ qua file binary / non-utf8
* đọc file text rồi ghi vào bundle

---

## 6.2 Export nhiều root vào cùng một bundle

```bash
copyast export \
  --root-dir app=../auto-asset-tool \
  --root-dir ci=../gitlab-ci \
  --export ./copyast-output.txt
```

---

## 6.3 Export và append thêm vào bundle cũ

```bash
copyast export \
  --root-dir app=../auto-asset-tool \
  --root-dir ci=../gitlab-ci \
  --export ./copyast-output.txt \
  --append
```

Nếu path đã tồn tại trong bundle thì entry sẽ được update.
Nếu path chưa tồn tại thì entry sẽ được thêm mới.

---

## 6.4 Import một hoặc nhiều file / directory vào bundle

### Import trực tiếp

```bash
copyast import \
  --root-dir . \
  --export ./copyast-output.txt \
  --file src/app/main.py \
  --dir src/app/application
```

Lệnh này sẽ:

* load bundle hiện tại
* tìm file / directory trong root
* nếu entry đã có thì update
* nếu chưa có thì thêm mới

### Import với nhiều root

```bash
copyast import \
  --root-dir app=../auto-asset-tool \
  --root-dir ci=../gitlab-ci \
  --export ./copyast-output.txt \
  --file src/app/main.py \
  --dir .github
```

Nếu cùng một relative path xuất hiện ở nhiều root thì mỗi root sẽ được lưu với prefix alias riêng.

---

## 6.5 Bulk import nhiều target

### Truyền trực tiếp

```bash
copyast bulk-import \
  --root-dir . \
  --export ./copyast-output.txt \
  --file src/app/main.py \
  --file src/app/domain/services.py \
  --dir tests
```

### Truyền qua list file

Ví dụ `targets.txt`:

```txt
file:src/app/main.py
file:src/app/domain/services.py
dir:tests
```

hoặc:

```txt
src/app/main.py
src/app/domain/services.py
tests/
```

rồi chạy:

```bash
copyast bulk-import \
  --root-dir . \
  --export ./copyast-output.txt \
  --list-file ./targets.txt
```

---

## 6.6 Delete một hoặc nhiều target khỏi bundle

```bash
copyast delete \
  --export ./copyast-output.txt \
  --file src/app/main.py
```

hoặc xóa theo directory:

```bash
copyast delete \
  --export ./copyast-output.txt \
  --dir tests
```

Lệnh này **chỉ xóa block trong bundle**, không xóa file thật ngoài filesystem.

---

## 6.7 Bulk delete

### Truyền trực tiếp

```bash
copyast bulk-delete \
  --export ./copyast-output.txt \
  --file src/app/main.py \
  --dir tests
```

### Truyền qua list file

```bash
copyast bulk-delete \
  --export ./copyast-output.txt \
  --list-file ./files-to-delete.txt
```

---

## 6.8 Delete theo substring path

```bash
copyast scan-delete \
  --export ./copyast-output.txt \
  --contains 'tests/'
```

Có thể lặp lại nhiều lần:

```bash
copyast scan-delete \
  --export ./copyast-output.txt \
  --contains 'tests/' \
  --contains '.idea/'
```

Ngoài `--contains`, command này cũng hỗ trợ `--file` và `--dir`.

---

## 6.9 Sync bundle theo Git

### Một repo

```bash
copyast sync-git \
  --root-dir . \
  --export ./copyast-output.txt
```

### Nhiều repo

```bash
copyast sync-git \
  --root-dir app=../auto-asset-tool \
  --root-dir ci=../gitlab-ci \
  --export ./copyast-output.txt
```

Lệnh này sẽ:

* kiểm tra từng `root-dir` có phải Git repo không
* đọc `git status --porcelain`
* import / update các file modified và untracked
* xóa các file deleted khỏi bundle

---

## 7. Ignore rules

`copyast` hiện hỗ trợ ignore từ:

* file ignore riêng qua `--ignore-file`
* `.gitignore`
* pattern thêm bằng `--ignore`

### Ví dụ `.copyastignore`

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
env/

build/
dist/
*.egg-info/
.eggs/

.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

.vscode/
.idea/
*.iml

.env
.env.*

bundle.txt
*.bundle.txt
*.png
*.jpg
*.pdf
*.zip
```

Project hiện có `.copyastignore.example` để làm mẫu. Có thể copy file đó thành `.copyastignore` rồi mở rộng thêm rule riêng cho project của mình.

---

## 8. Ví dụ thực tế

### Export 2 repo vào 1 bundle

```bash
copyast export \
  --root-dir app=../auto-asset-tool \
  --root-dir ci=../gitlab-ci \
  --export ./bundle.txt
```

### Append thêm nội dung vào bundle cũ

```bash
copyast export \
  --root-dir docs=../docs-repo \
  --export ./bundle.txt \
  --append
```

### Import thêm 1 file và 1 thư mục

```bash
copyast import \
  --root-dir app=../auto-asset-tool \
  --export ./bundle.txt \
  --file src/app/main.py \
  --dir src/app/application
```

### Sync theo Git cho nhiều repo

```bash
copyast sync-git \
  --root-dir app=../auto-asset-tool \
  --root-dir ci=../gitlab-ci \
  --export ./bundle.txt
```

---

## 9. Cleanup code (optional)

```bash
pip install black isort ruff
ruff check . --fix
isort .
black .
```