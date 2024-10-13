FROM odoo:18.0

USER root
RUN apt-get update
RUN apt-get install -y black npm
RUN npm install -g prettier
USER odoo
