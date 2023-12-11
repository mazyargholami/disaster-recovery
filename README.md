# Disaster Recovery

## Nginx configurations
    http {
        upstream backend {
            server api.fidauth.com max_fails=3 fail_timeout=30s;
            server develop.fidauth.com max_fails=3 fail_timeout=30s;
            # Add more servers as needed
        }
    
        server {
            listen 80;
            server_name fidauth.com;
            return 301 https://$host$request_uri;
        }
    
        server {
            listen 443 ssl;
            server_name fidauth.com;
    
            ssl_certificate /path/to/ssl/certificate.crt;
            ssl_certificate_key /path/to/ssl/private.key;
            ssl_protocols TLSv1.2 TLSv1.3;
            ssl_ciphers 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384';
    
            location / {
                proxy_pass http://backend;
                # Other proxy settings as needed
            }
    
            # Health check endpoint for api.fidauth.com
            location /health-api {
                access_log off;
                proxy_pass http://api.fidauth.com;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
    
            # Health check endpoint for develop.fidauth.com
            location /health-develop {
                access_log off;
                proxy_pass http://develop.fidauth.com;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
    }
