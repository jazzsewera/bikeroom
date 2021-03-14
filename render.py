import argparse
import pandas as pd
from pathlib import Path
from subprocess import run


def read_csv(file):
    return (pd
            .read_csv(file, sep=' *; *', header=0, dtype=str, engine='python')
            .to_dict('records'))


def format_full(data):
    return '\n'.join([f'{record["hook"]} '
                      f'& {record["lastname"]} '
                      f'& {record["firstname"]} '
                      f'& {record["room"]} '
                      f'& {record["telephone"]} '
                      r'\\ \hline'
                      for record in data])


def format_reduced(data):
    return '\n'.join([f'{record["hook"]} '
                      f'& {record["lastname"]} '
                      f'& {record["firstname"]} '
                      r'\\ \hline'
                      for record in data])


def apply_template(template_file, data, year_type, year, formatter):
    with open(template_file, mode='r') as _t:
        template_lines = _t.read()
    template = ''.join(template_lines)
    return (template
            .replace('{{data}}', formatter(data))
            .replace('{{type}}', year_type)
            .replace('{{year}}', year))


def write_document(document_file, document_content):
    document_file.parent.mkdir(parents=True, exist_ok=True)
    with open(document_file, mode='w') as _f:
        _f.write(document_content)


def generate_pdf(document_file, output_file):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    run(['pdflatex',
         '-output-directory',
         output_file.parent.resolve(),
         document_file.resolve()])


def main():
    argp = argparse.ArgumentParser(description='Render Bike room lists. '
                                   'data.csv + templates = lists')

    argp.add_argument('--holidays', '--summer', '--wakacje', '-s', '-w',
                      action='store_true', dest='holidays')
    argp.add_argument('--year', '--rok', '-y', '-r',
                      required=True, dest='year')

    args = argp.parse_args()

    # Parameters
    # # Year type: [holidays | university year]
    if args.holidays:
        year_type = 'wakacje'
    else:
        year_type = 'rok akademicki'

    # # Year: [2020 | 2020/2021 | ...]
    year = args.year

    # Files
    # # Input files
    # ## Data
    data_file = Path('./data/data.csv')
    # ## Templates
    full_template = Path('./tex/full.template.latex')
    reduced_template = Path('./tex/reduced.template.latex')

    # # Output files
    # ## Generated LaTeX
    full_document = Path('./out/full.latex')
    reduced_document = Path('./out/reduced.latex')

    # ## Rendered PDFs
    full_pdf = Path('./out/rendered/full.pdf')
    reduced_pdf = Path('./out/rendered/reduced.pdf')

    # Steps
    # # Read data from csv
    data = read_csv(data_file)

    # # Generate document content from templates
    full_content = apply_template(full_template, data, year_type, year,
                                  format_full)
    reduced_content = apply_template(reduced_template, data, year_type, year,
                                     format_reduced)

    # # Write generated LaTeX to files
    write_document(full_document, full_content)
    write_document(reduced_document, reduced_content)

    # # Generate PDFs from LaTeX
    generate_pdf(full_document, full_pdf)
    generate_pdf(reduced_document, reduced_pdf)


if __name__ == "__main__":
    main()
