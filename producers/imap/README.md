# IMAP producer for ReceiptsTracker

Imap producer polls messages every N minutes and sends them to ReceiptsTracker
backend API.

Here's an example configuration file `imap_handler.ini`:

	[IMAP]
	login_name=myreceiptslogin
	password=thisisverysecret
	folder=receipts
	server_address=imap.emailprovider.com

	[Messages]
	delete_after_n_days=30

	[Receipts_api]
	server_address=http://localhost:5555

TODO:

	[ ] Polling (or just use cron?)
