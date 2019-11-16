# Receipts Tracker API

An API for tracking receipts.

Supports the following features:

	* Tagging

	* Reads texts from the receipts

	* Store purchase date

	* Calculate expiration day


## Dependencies

* Python 3

* Flask

* Dateutil


## Usage
### Running receipts_api.py
`receipts_api.py` has the following options available:

| Option | Description         |
| ------ | ------------------- |
| -c	 | Configuration file  |
| -d	 | Debug mode          |


### Sending receipt images to API
Send `myreceipt.png` file with the tags `laptop`, `lenovo`, `2017-01-13` and
`1_year`.
Purchase date will be automatically parsed from the second last tag and
expiration tag calculated from the last tag.

	curl -i -X POST -F "file=@myreceipt.png" \
		-F "tags=laptop lenovo 2017-01-13 1_year" \
		localhost:5555


### Special tags
There are special tags that can be used to inform the following things:

| Tag example | Format                | Default         | Description             |
| ----------- | --------------------- | --------------- | ----------------------- |
| 2019-01-30  | `%Y-%m-%d`            | Current date    | Set the purchase date   |
| 3\_years    | `n_(day\|days\|month\|months\|year\|years)` | None | Set the expiration time |

