FROM watchdogs:latest

ENV WATCHDOG_CONFIG_LOCATION /app/config.py

# Copy our custom config into place
COPY config.py /app/config.py

# Link in specific tests to enable them to run when the container starts
RUN for test in \
        github_hooks \
        github_public_repos \
        github_users \
            ; do ln -s /app/available_tests/test_${test}.py /app/enabled_tests/test_${test}.py; done
