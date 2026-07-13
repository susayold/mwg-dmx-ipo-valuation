# Contributing

Cảm ơn bạn muốn cải thiện MWG–DMX IPO Valuation Lab. Repository ưu tiên tính truy vết, khả năng tái tạo và phân biệt rõ giữa dữ liệu công bố, dự phóng của doanh nghiệp và giả định của analyst.

## Nguyên tắc dữ liệu

1. Chỉ dùng nguồn chính thức của tổ chức phát hành, cơ quan quản lý hoặc sở giao dịch cho các facts trọng yếu.
2. Thêm mọi nguồn vào `data/source_registry.csv` với URL, kỳ, scope, audit status, thời điểm truy xuất và SHA-256.
3. Không commit PDF/XLSX gốc vào `data/raw/` hoặc vị trí khác. Không tái phân phối tài liệu khi chưa có quyền.
4. Không trộn báo cáo consolidated với separate, reported với pro forma, actual với management outlook.
5. Giữ `source_id` cho từng fact; không sửa một số reported để làm cho model cân.
6. Nếu thay đổi perimeter, phải cập nhật `docs/data_scope.md` và chứng minh không double-count EraBlue.

## Thiết lập môi trường

```bash
npm ci
python -m pip install -e "analytics[xlsx]"
python -m pip install -r requirements-artifacts.txt
```

## Kiểm tra trước pull request

```bash
npm test
python -m unittest discover -s analytics/tests -v
python scripts/build_financial_model.py
python scripts/build_reports.py
```

Pull request nên mô tả nguồn mới/thay đổi assumption, ảnh hưởng đến perimeter hoặc valuation, và kết quả test. Nếu output artifact thay đổi, nêu rõ input nào làm thay đổi hash.

## Quy ước thay đổi model

- Input có thể chỉnh phải được nhận diện rõ; formula và cross-sheet links không được hard-code thành output.
- Thêm check cho mọi bridge quan trọng và giữ publication gate đối với target price/rating.
- Scenario phải có đơn vị và cơ sở ownership nhất quán.
- Không dùng dữ liệu synthetic làm official actuals.

## Phạm vi giấy phép

Bằng việc đóng góp, bạn đồng ý phát hành phần mã/nội dung nguyên bản của mình theo MIT License. Không gửi tài liệu hoặc nội dung của bên thứ ba nếu bạn không có quyền cấp phép. Đây không phải tư vấn đầu tư hoặc tư vấn pháp lý.
