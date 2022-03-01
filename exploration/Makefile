open:
	@open temp/html/`ls temp/html/* | sort -n | tail -1 | cut -d '.' -f1`/`ls temp/html/* | sort -n | tail -1 | cut -d '.' -f1`.html

clean:
	@rm -rf temp/csv/*.csv temp/html/*
	@echo "Deleted temporary files."