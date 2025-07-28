# 本脚本用来停止/启动/重启守护进程中的服务

# 拷贝配置文件
cp -f poultrygpt.service /etc/systemd/system/

# 停止服务
sudo systemctl stop poultrygpt.service

# 禁用服务（如果需要）
sudo systemctl disable poultrygpt.service

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（如果之前禁用了）
sudo systemctl enable poultrygpt.service

# 启动服务
sudo systemctl start poultrygpt.service

# 检查服务状态
sudo systemctl status poultrygpt.service