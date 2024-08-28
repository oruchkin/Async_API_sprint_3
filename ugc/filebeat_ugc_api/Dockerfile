FROM docker.elastic.co/beats/filebeat:8.5.3

COPY filebeat.yml /usr/share/filebeat/filebeat.yml

USER root
RUN chown root:filebeat /usr/share/filebeat/filebeat.yml

ENTRYPOINT ["/usr/share/filebeat/filebeat", "-e", "-strict.perms=false", "-c", "/usr/share/filebeat/filebeat.yml"]
