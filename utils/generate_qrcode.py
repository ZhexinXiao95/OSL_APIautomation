import qrcode

# 替换为您的 Google Drive 文件链接
file_link = "https://artifacts.bct.host/repository/osl-storage-public/apk/debug/app-debug.apk"
yunshu_link = "https://drive.google.com/file/d/1a8W5x9UbyZv_JEZcpwEk6Gw4orozNzoZ/view?usp=sharing"
# 生成二维码
qr = qrcode.make(file_link)

# 保存二维码图像
qr.save("/Users/shawn.xiao/PycharmProjects/pythonProject4/app_package/andriod.png")
