"""简单Cookie导出工具"""
# 使用方法:
# 1. 打开 https://youtube.com 并登录
# 2. 在浏览器控制台执行以下JS获取cookie:

"""
javascript:(function(){
  let cookies = document.cookie.split(';');
  let cookieStr = '';
  for(let c of cookies){
    let [k,v] = c.trim().split('=');
    cookieStr += k + '=' + v + '; ';
  }
  copy(cookieStr);
  alert('Cookie copied to clipboard!');
})()
"""

# 或者使用以下在线工具:
# https://cookie-editor.cglled.ch/
# 导出格式选择 "Netscape HTTP Cookie File"

print("请使用以下方法获取Cookie:")
print("1. Chrome安装 'Get cookies.txt LOCALLY' 扩展")
print("2. 访问 youtube.com 并登录")
print("3. 点击扩展 -> Export -> Cookies.txt")
print("4. 保存到项目根目录: E:\\vibe coding\\CC\\download 视频\\content-summarizer\\cookies.txt")
