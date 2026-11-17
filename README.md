# myyoutube - quản trị kênh @thayhungp

- Laptop = phòng giám đốc (ra quyết định, sản xuất video, chạy lệnh sửa/xóa)
- Blogger = công xưởng (bài học + video nhúng, phụ huynh vào xem) và quầy dẫn khách sang YouTube
- GitHub = đội công nhân và kỹ sư (tự kiểm kho, thống kê, soạn bài mẫu mỗi ngày)
- YouTube = cửa hàng chính (nơi xây kênh, khách xem + đăng ký)

Lệnh hay dùng (trong thư mục này, PowerShell):
    .\run.ps1 sync        # đồng bộ video, chủ đề, trùng lặp, phân tích, marketing
    .\run.ps1 lessons     # kiểm kho bài học Blogger <-> video YouTube
    .\run.ps1 money       # tiến độ kiếm tiền
    .\run.ps1 auth        # đăng nhập Google (làm 1 lần để sửa/xóa video)
    .\run.ps1 edit VIDEO_ID --title "Tiêu đề mới"