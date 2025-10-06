FROM odoo:14.0

USER root

# Copy requirements and install
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Copy all custom addons (current directory contains addon folders)
COPY . /mnt/extra-addons

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user
USER odoo

# Expose Odoo port
EXPOSE 8069

# Start Odoo
CMD ["odoo"]
