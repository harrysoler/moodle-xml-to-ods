import xml.etree.ElementTree as ET

from xmlparse import extract_questions_from


def main():
    tree = ET.parse("./test.xml")
    root = tree.getroot()

    # logging.getLogger().setLevel(logging.DEBUG)

    questions = extract_questions_from(root)
    print(questions)

if __name__ == "__main__":
    main()
