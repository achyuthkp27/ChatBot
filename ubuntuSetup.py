#To copy files/folders
# scp -i ".\flask-app.pem" .\requirements.txt ubuntu@ec2-16-171-226-5.eu-north-1.compute.amazonaws.com:/home/ubuntu/helloworld

    # ssh -i "flask-app.pem" ubuntu@ec2-16-171-226-5.eu-north-1.compute.amazonaws.com
    # python3 -m venv venv
    # source venv/bin/activate

# sudo nano /etc/systemd/system/helloworld.service

# sudo systemctl daemon-reload
# sudo systemctl start helloworld
# sudo systemctl enable helloworld

#To restart if any changes made
# sudo systemctl restart helloworld.service

# sudo systemctl start nginx
# sudo systemctl enable nginx

#To make nginx changes
# sudo nano /etc/nginx/sites-available/default

# To restart nginx
# sudo systemctl restart nginx