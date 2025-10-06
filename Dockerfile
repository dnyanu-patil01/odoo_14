FROM odoo:14.0

USER root

# Copy requirements and install
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Copy custom addons if any
COPY ./addons /mnt/extra-addons

# Switch back to odoo user
USER odoo

# Expose Odoo port
EXPOSE 8069
