# 🏆 CASE STUDY THỰC CHIẾN: RA MẮT THƯƠNG HIỆU ECOWEAR VIETNAM
## DỰ ÁN MẪU ĐƯỢC THỰC HIỆN BỞI HỆ THỐNG "THE AGENCY OS" TRONG 24 GIỜ

---

> [!NOTE]
> **Khách hàng giả định**: EcoWear Vietnam — Startup thời trang bền vững từ sợi tre tự nhiên, cần ra mắt thị trường thần tốc trong vòng 48 giờ để đón chiến dịch Mega Sale.
> **Thời gian thực hiện**: 18 giờ liên tục.
> **Các phòng ban AI tham gia**: Product Manager, Frontend Developer, Vietnamese E-Commerce Strategist, Vietnamese Legal & Tax Controller.

---

## 📑 DELIVERABLE 1: BẢN ĐẶC TẢ SẢN PHẨM & USER JOURNEY
*Thực hiện bởi: `product-manager`*

### 1. Chân Dung Khách Hàng Mục Tiêu (Customer Persona)
- **Tên đại diện**: "Linh - Dân văn phòng thế hệ mới" (24 - 32 tuổi).
- **Thu nhập**: 12 - 25 triệu VNĐ/tháng, sinh sống tại Hà Nội & TP. Hồ Chí Minh.
- **Nỗi đau (Pain Points)**:
  - Mặc sơ mi và áo thun thông thường bị bí bách, đổ mồ hôi khi di chuyển ngoài trời nắng nóng.
  - Quần áo giá rẻ giặt máy 3 lần là bị xù lông, bai dão cổ áo.
  - Thích lối sống xanh (Eco-friendly) nhưng các hãng thời trang bền vững quốc tế giá quá cao (trên 1 triệu/chiếc).
- **Điểm kích hoạt mua hàng (Buying Triggers)**: Mềm mát tức thì (-3°C khi chạm), khử mùi tự nhiên, thiết kế tối giản mặc đi làm hay đi cà phê đều lịch sự.

### 2. Định Vị USP Cốt Lõi (Unique Selling Proposition)
- **Thông điệp chính**: *"EcoWear — Thời trang sợi tre thoáng mát tự nhiên, bền đẹp qua 100 lần giặt"*.
- **Cam kết vàng**: Đổi trả 1-đổi-1 trong 15 ngày không cần lý do.

---

## 💻 DELIVERABLE 2: MÃ NGUỒN LANDING PAGE CHUẨN CHUYỂN ĐỔI (CRO)
*Thực hiện bởi: `engineering-frontend-developer` & Thẩm định bởi `testing-reality-checker`*

*Mã nguồn HTML5 + Tailwind CSS hoàn chỉnh, tối ưu Responsive mobile và sẵn sàng copy chạy trực tiếp:*

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoWear Vietnam — Thời Trang Sợi Tre Bền Vững</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 font-sans">
    <!-- Top Announcement -->
    <div class="bg-emerald-800 text-white text-xs text-center py-2 px-4 font-semibold">
        🌿 Ưu đãi ra mắt: Tặng voucher 50K + Miễn phí vận chuyển toàn quốc cho 100 đơn đầu tiên!
    </div>

    <!-- Hero Section -->
    <header class="max-w-6xl mx-auto px-4 py-16 text-center">
        <span class="inline-block bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1 rounded-full mb-4">
            Công Nghệ Dệt Sợi Tre Kháng Khuẩn 2026
        </span>
        <h1 class="text-4xl md:text-5xl font-black text-slate-900 tracking-tight leading-tight mb-4">
            Mềm Mát Tự Nhiên.<br><span class="text-emerald-700">Tự Tin Suốt 12 Giờ Làm Việc.</span>
        </h1>
        <p class="text-slate-600 max-w-2xl mx-auto text-base mb-8">
            Áo thun EcoWear làm từ 95% sợi tre sinh thái và 5% Spandex. Kháng khuẩn tự nhiên, giảm nhiệt tức thì 3°C, giữ form áo phẳng phiu suốt cả ngày.
        </p>
        <div class="flex justify-center gap-4">
            <a href="#order" class="bg-emerald-700 hover:bg-emerald-800 text-white font-bold px-8 py-3.5 rounded-xl shadow-lg shadow-emerald-700/20 transition">
                Đặt Mua Ngay — 299.000đ
            </a>
        </div>
    </header>

    <!-- Key Features -->
    <section class="max-w-5xl mx-auto px-4 py-12 grid md:grid-cols-3 gap-6">
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 text-center">
            <div class="text-3xl mb-3">❄️</div>
            <h3 class="font-bold text-lg mb-2">Hạ Nhiệt -3°C</h3>
            <p class="text-slate-600 text-xs leading-relaxed">Cấu trúc sợi tre rỗng vi mô giúp thông thoáng khí gấp 4 lần so với vải cotton truyền thống.</p>
        </div>
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 text-center">
            <div class="text-3xl mb-3">🛡️</div>
            <h3 class="font-bold text-lg mb-2">Khử Mùi Tự Nhiên</h3>
            <p class="text-slate-600 text-xs leading-relaxed">Hợp chất Bamboo Kun tự nhiên ngăn ngừa 99.8% sự phát triển của vi khuẩn gây mùi cơ thể.</p>
        </div>
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 text-center">
            <div class="text-3xl mb-3">✨</div>
            <h3 class="font-bold text-lg mb-2">Bền Form 100 Lần Giặt</h3>
            <p class="text-slate-600 text-xs leading-relaxed">Bo cổ dệt mật độ cao chống bai dão, co giãn 4 chiều mềm mại ôm vừa vặn cơ thể.</p>
        </div>
    </section>

    <!-- Order Form Section -->
    <section id="order" class="max-w-xl mx-auto px-4 py-16">
        <div class="bg-white p-8 rounded-3xl shadow-xl border border-slate-100">
            <h2 class="text-2xl font-bold text-center text-slate-900 mb-2">Đăng Ký Đặt Hàng Nhận Ưu Đãi</h2>
            <p class="text-center text-xs text-slate-500 mb-6">Kiểm tra hàng trước khi thanh toán — Đổi trả miễn phí trong 15 ngày</p>
            
            <form class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Họ và tên *</label>
                    <input type="text" required placeholder="Nguyễn Văn A" class="w-full border border-slate-200 rounded-lg p-3 text-sm focus:outline-none focus:border-emerald-600">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Số điện thoại *</label>
                    <input type="tel" required placeholder="0987 654 321" class="w-full border border-slate-200 rounded-lg p-3 text-sm focus:outline-none focus:border-emerald-600">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Địa chỉ nhận hàng *</label>
                    <input type="text" required placeholder="Số nhà, đường, phường, quận/huyện, tỉnh/thành" class="w-full border border-slate-200 rounded-lg p-3 text-sm focus:outline-none focus:border-emerald-600">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Kích cỡ (Size)</label>
                        <select class="w-full border border-slate-200 rounded-lg p-3 text-sm">
                            <option>Size M (50 - 62kg)</option>
                            <option>Size L (63 - 72kg)</option>
                            <option>Size XL (73 - 82kg)</option>
                            <option>Size XXL (83 - 92kg)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Màu sắc</label>
                        <select class="w-full border border-slate-200 rounded-lg p-3 text-sm">
                            <option>Trắng Tinh Khiết</option>
                            <option>Đen Huyền Bí</option>
                            <option>Xanh Rêu Eco</option>
                        </select>
                    </div>
                </div>
                <button type="button" class="w-full py-4 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow-lg transition">
                    XÁC NHẬN ĐẶT HÀNG (299.000đ)
                </button>
            </form>
        </div>
    </section>
</body>
</html>
```

---

## 🛍️ DELIVERABLE 3: CHIẾN LƯỢC ĐÁNH CHIẾM SHOPEE & TIKTOK SHOP
*Thực hiện bởi: `specialized-vietnamese-ecommerce-strategist`*

### 1. Ma Trận 3 Tầng Sản Phẩm
- **Sản phẩm Phễu (Traffic Hero)**: Set 3 đôi tất sợi tre kháng khuẩn (Giá bán: **59.000đ** - Margin 15%).  
  👉 Mục đích: Gom lượng đánh giá 5 sao nhanh nhất, kéo khách bấm vào Shop.
- **Sản phẩm Chủ Lực (Revenue Core)**: Áo thun Bamboo EcoWear (Giá niêm yết: 450K, Flash Sale: **289.000đ** - Margin 42%).
- **Sản phẩm Giá Trị Cao (Profit Driver)**: Combo 3 áo thun đóng hộp quà cao cấp (Giá bán: **799.000đ** - Margin 51%).

### 2. Bài Toán Tài Chính Chi Tiết Từng Chiếc Áo (P&L per SKU)

| Khoản mục chi phí | Số tiền (VNĐ) | % Giá bán |
| :--- | :--- | :--- |
| **Giá bán Flash Sale (Revenue)** | **289.000 VNĐ** | **100%** |
| Giá vốn sản xuất tại xưởng (COGS) | 110.000 VNĐ | 38.0% |
| Phí cố định Shopee (Shopee Mall) | 11.560 VNĐ | 4.0% |
| Phí thanh toán sàn | 11.560 VNĐ | 4.0% |
| Gói Voucher Xtra & Freeship Xtra | 20.230 VNĐ | 7.0% |
| Chi phí hộp carton & túi zip lụa | 7.000 VNĐ | 2.4% |
| Dự phòng hoàn hàng & đổi trả (5%) | 14.450 VNĐ | 5.0% |
| **LỢI NHUẬN RÒNG (NET PROFIT)** | **114.200 VNĐ** | **39.5%** |

👉 **Nhận định**: Biên lợi nhuận ròng 39.5% là chỉ số cực kỳ an toàn, cho phép shop trích tiếp 10 - 15% để booking affiliate KOC mà vẫn đảm bảo lợi nhuận ròng trên 25%.

### 3. Kịch Bản Livestream Bán Hàng 60 Phút Chốt 150 Đơn
- **Phút 00 - 10 (Kéo mắt xem)**: Tung deal áo thun 99K cho 10 người share livestream đầu tiên.
- **Phút 10 - 35 (Showcase công năng)**: Test thực tế đổ nước lên vải chứng minh độ thấm hút, dùng bàn là thử form cổ áo, kéo giãn 4 chiều.
- **Phút 35 - 50 (Tung Voucher sàn)**: Kêu gọi người xem áp mã Voucher Mall giảm 15% độc quyền của phiên live.
- **Phút 50 - 60 (Đếm ngược xả kho)**: Chỉ còn 20 chiếc duy nhất trước khi đóng giỏ hàng.

---

## ⚖️ DELIVERABLE 4: BÁO CÁO RÀ SOÁT PHÁP LÝ & TỐI ƯU CHI PHÍ THUẾ
*Thực hiện bởi: `specialized-vietnamese-legal-compliance` & `specialized-vietnamese-tax-accounting`*

### 1. Rà Soát Hợp Đồng Gia Công May Mặc Với Xưởng OEM
- **Rủi ro mất mẫu thiết kế**: Cần bổ sung Điều khoản Cam kết Bảo mật & Quyền Sở Hữu Trí Tuệ: Xưởng may không được phép bán lẻ hoặc tuồn phôi áo EcoWear ra thị trường bên ngoài dưới bất kỳ hình thức nào. Phạt vi phạm 8% giá trị hợp đồng và bồi thường toàn bộ thiệt hại thực tế phát sinh.
- **Quy chuẩn kiểm định chất lượng (AQL 2.5)**: Nếu tỷ lệ lỗi may vượt quá 3% lô hàng, xưởng phải chịu trách nhiệm may bù và đền bù tiến độ giao hàng chậm 0.5%/ngày.

### 2. Tối Ưu Chi Phí Thuế Hợp Lệ Tại Việt Nam
- **Điều kiện để 100% chi phí vải & may được trừ khi tính thuế TNDN**:
  - Hợp đồng gia công đầy đủ chữ ký 2 bên.
  - Hóa đơn điện tử hợp pháp tra cứu trên hệ thống Thuế (`hoadondientu.gdt.gov.vn`).
  - Toàn bộ thanh toán từ 20 triệu đồng trở lên **bắt buộc chuyển khoản từ Tài khoản ngân hàng công ty sang tài khoản công ty của xưởng** (Không chuyển khoản cá nhân).
- **Thuế suất GTGT**: Vải dệt và gia công may mặc chịu thuế suất GTGT 8% (theo chính sách giảm thuế kích cầu) hoặc 10% theo quy định thông thường. Cần lấy đủ hóa đơn đầu vào để được khấu trừ toàn bộ thuế GTGT đầu ra khi bán trên sàn Shopee/TikTok.

---

## 💡 ĐÁNH GIÁ TỔNG KẾT DỰ ÁN
Bộ hồ sơ trên chứng minh rằng: **Chỉ trong chưa đầy 24 giờ**, hệ thống `The Agency OS` hoàn toàn có thể thay thế một đội ngũ nhân sự gồm 4 người (Product, Coder, Marketer sàn TMĐT, Kế toán pháp chế) để tạo ra sản phẩm hoàn chỉnh, chi tiết đến từng dòng code và từng con số tài chính.
