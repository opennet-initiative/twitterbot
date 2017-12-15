include makefilet-download-ondemand.mk

default: help

help: help-on-twitterbot

.PHONY: help-on-twitterbot
help-on-twitterbot:
	@echo "on-twitterbot packaging targets:"
	@echo "    deploy-deb-remote"
	@echo "    style"
	@echo

.PHONY: deploy-deb-remote
deploy-deb-remote: dist-deb-packages-directory
	@if [ -z "$(DEPLOY_TARGET)" ]; then \
		echo >&2 "Missing 'DEPLOY_TARGET' environment variable (e.g. 'root@jun.on')."; \
		exit 1; fi
	scp "$(DIR_DEBIAN_SIMPLIFIED_PACKAGE_FILES)"/*.deb "$(DEPLOY_TARGET):/tmp/"
	ssh "$(DEPLOY_TARGET)" \
		'for fname in on-twitterbot; do \
			dpkg -i "/tmp/$$fname.deb" && rm "/tmp/$$fname.deb" || exit 1; done'
