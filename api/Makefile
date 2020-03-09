HOST		:= localhost
PORT		:= 5555
UPLOADS_DIR	:= uploads


.PHONY: clean-db clean-uploads send-* test

init:
	if [ ! -d $(UPLOADS_DIR) ]; then mkdir $(UPLOADS_DIR); fi

clean-db:
	sqlite3 receipts.db "DELETE FROM receipt;"
	sqlite3 receipts.db "DELETE FROM tag;"
	sqlite3 receipts.db "DELETE FROM receipt_tag_association;"
	sqlite3 receipts_test.db "DELETE FROM receipt;"
	sqlite3 receipts_test.db "DELETE FROM tag;"
	sqlite3 receipts_test.db "DELETE FROM receipt_tag_association;"

clean-uploads:
	rm -f uploads/*

test: clean-db clean-uploads \
	send-with-date-and-expiration post-check

post-check:
	@echo "Receipt"
	sqlite3 receipts.db "SELECT * FROM receipt;"
	@echo "Tag"
	sqlite3 receipts.db "SELECT * FROM tag;"
	@echo "Association"
	sqlite3 receipts.db "SELECT * FROM receipt_tag_association;"

generate-random-file:
	dd if=/dev/urandom of=blargh.png bs=1K count=1 >/dev/null 2>&1

send-without-date: generate-random-file
	curl -i -X POST -F "file=@blargh.png" \
		-F "tags=hieno ensimmäinen tiedosto" \
		$(HOST):$(PORT)

send-with-date-and-expiration: generate-random-file
	curl -i -X POST -F "file=@blargh.png" \
		-F "tags=hieno ensimmäinen 2017-01-13 1_year tiedosto" \
		$(HOST):$(PORT)

send-with-date-and-expiration-remote: generate-random-file
	curl -i -X POST -F "file=@blargh.png" \
		-F "tags=hieno ensimmäinen 2017-01-13 1_year tiedosto" \
		$(HOST):$(PORT)/receipts/


send-two-times: generate-random-file
	curl -i -X POST -F "file=@blargh.png" \
		-F "tags=2017-01-13 1_year" \
		$(HOST):$(PORT)
	curl -i -X POST -F "file=@blargh.png" \
		-F "tags=2017-01-13 1_year" \
		$(HOST):$(PORT)

