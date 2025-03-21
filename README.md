sudo systemctl restart adeeny-api.service

sudo systemctl restart adeeny-api.service
sudo systemctl status adeeny-api.service

sudo systemctl daemon-reload

sudo systemctl restart nginx

sudo systemctl status nginx

watch -d -n 1 systemctl status adeeny-api.service