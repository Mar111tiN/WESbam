from coverage import get_cover_svg

import os


def main(s):

    workdir = s.config["workdir"]
    input = s.input
    output = os.path.join(workdir, str(s.output))

    params = s.params
    w = s.wildcards
    get_cover_svg(
        input.sample,
        output,
        sample=w.sample,
        exon_cover=params.exon_cover,
        refgen=params.refgen,
        log=s.log,
        prettifyBed=params.prettifyBed,
    )


if __name__ == "__main__":
    main(snakemake)
