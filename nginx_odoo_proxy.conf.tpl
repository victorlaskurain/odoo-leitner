upstream odoo {
    server odoo:8069;
}
upstream odoochat {
    server odoo:8072;
}
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen       80;
    listen  [::]:80;
    server_name  $SERVER_NAME;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_read_timeout 720s;

    client_max_body_size 100M;

    # Add Headers for odoo proxy mode
    proxy_set_header X-Forwarded-Host $host:$HTTP_PORT;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # Redirect websocket requests to odoo gevent port
    location /websocket {
        proxy_pass http://odoochat;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Redirect requests to odoo backend server
    location / {
        proxy_pass http://odoo;
        proxy_redirect http://odoo http://$host:$HTTP_PORT;
    }

    # common gzip
    gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;
    gzip on;
}
