# Nginx Configurations

<p align="center" ><img width=400 src="../assets/pngegg (1).png"> </p>

## Version Control:
#### Objective:
- Keep Nginx configuration files under version control using tools like Git. This enables easy rollback to a known working state.

      # Initialize a Git repository for Nginx configuration files
      cd /etc/nginx/
      git init
      
      # Add and commit changes
      git add .
      git commit -m "Initial commit"
      
      # Rollback to a specific commit if needed
      git log  # Identify commit hash
      git revert <commit-hash>


## Use Nginx as a Load Balancer:
  - Set up Nginx as a load balancer to distribute incoming traffic across multiple backend servers. This can be achieved using the upstream directive in your Nginx configuration.

        http {
            upstream backend {
                server backend1.example.com;
                server backend2.example.com;
                # Add more servers as needed
            }
        
            server {
                listen 80;
                server_name yourdomain.com;
        
                location / {
                    proxy_pass http://backend;
                    # Other proxy settings as needed
                }
            }
        }

## Configure Health Checks:
  - Implement health checks to monitor the status of your backend servers. Nginx can periodically send requests to check the health of each server and route traffic only to healthy servers.

        http {
            upstream backend {
                server backend1.example.com max_fails=3 fail_timeout=30s;
                server backend2.example.com max_fails=3 fail_timeout=30s;
                # Add more servers as needed
            }
        
            server {
                listen 80;
                server_name yourdomain.com;
        
                location / {
                    proxy_pass http://backend;
                    # Other proxy settings as needed
                }
        
                # Health check endpoint
                location /health {
                    access_log off;
                    proxy_pass http://backend;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                }
            }
        }
