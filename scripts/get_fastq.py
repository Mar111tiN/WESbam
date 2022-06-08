import os
from os import system as shll
from script_utils import show_output


def main(s):
    input = s.input
    output = s.output
    threads = s.threads

    extension = os.path.splitext(input[0])[1]
    if extension == '.fastq':
        # compress fastq as fastq.gz into workdir
        shll(f"pigz -5 -p {threads} {input} > {output}")
    elif extension == '.gz':
        show_output(f"Creating symlink for file {input}")
        # create shortcut to fastq.gz in workdir/fastq
        shll(f"ln -s {input} {output}")
    elif extension == '.bz2':
        show_output(f"file extension {extension} --> unzipping with bzcat")
        # uncompress fastq.b2 and recompress to fastq.gz in workdir/fastq
        shll(f"bzcat {input} | pigz -5 -p {threads} > {output}")


if __name__ == "__main__":
    main(snakemake)
