# Concordia Schedule Export v2

Easily export your Concordia class schedule to a `.ics` file for seamless import into your favorite calendar apps, such as `Apple Calendar` or `Google Calendar`.

**Note:** This script is an updated and enhanced version of an old [script](https://github.com/MatteoGisondi/ConcordiaScheduleExport) from **3 years ago**.

Shoutout to [Matteo Gisondi](https://matteo.gisondi.site/) for the **inspiration**, and thanks to [Yannis OUAKRIM](https://github.com/Yojda) for **testing**.

## Getting Started

This script requires **Python**. If you don’t have Python installed, follow [this tutorial](https://kinsta.com/knowledgebase/install-python/) for instructions on installing Python on **Windows**, **macOS**, or **Linux**.

## Installation

1. **Clone** or **download** the repository.
2. Open a terminal in the **project directory**.
3. **Run** the following command to install the required dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Usage


https://github.com/user-attachments/assets/5e0302d9-c047-40c7-bb42-f522de06e9ad

## Steps to Export Your Schedule

1. Go to [Concordia website](https://www.concordia.ca/).
2. Navigate to **Student Center**.
3. On the homepage, click on `Weekly Schedule`.
4. Select your term and click **Continue**.
5. Right-click anywhere on the page and select **Inspect**.
6. In the Inspector window, search for the table containing your schedule (as shown in the video).
8. Right-click on the table’s HTML element and select **Copy > Copy outerHTML**.
9. In the repository folder, open the file named myconcordia.html and paste the copied table’s HTML content.
10. Run the script using the following command: `python3 main.py`

## Contributing

This version is currently in **beta**, and we welcome any contributions. If you’d like to make changes, please submit a **pull request**.

If you find this script helpful, consider leaving a ⭐️! Thank you for your support ❤️.

## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License.
