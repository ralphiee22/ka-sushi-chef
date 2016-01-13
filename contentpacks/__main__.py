
"""
makepack

Usage:
  makecontentpacks ka-lite <lang> <version> [--subtitlelang=subtitle-lang --contentlang=content-lang --interfacelang=interface-lang --videolang=video-lang --out=outdir]
  makecontentpacks -h | --help
  makecontentpacks --version

"""
from docopt import docopt
from pathlib import Path

from contentpacks.khanacademy import retrieve_language_resources, apply_dubbed_video_map, retrieve_html_exercises
from contentpacks.utils import translate_nodes, flatten_topic_tree, \
    remove_untranslated_exercises, bundle_language_pack, separate_exercise_types, \
    generate_kalite_language_pack_metadata


def make_language_pack(lang, version, sublangargs, filename):

    topic_data, content_data, exercise_data, subtitles, interface_catalog, content_catalog, dubmap = retrieve_language_resources(version, sublangargs)

    node_data = list(
        flatten_topic_tree(topic_data, content_data, exercise_data)
    )

    node_data = translate_nodes(node_data, content_catalog)
    node_data = list(node_data)
    # node_data = list(
    #     apply_dubbed_video_map(node_data, dubmap)
    # )

    html_exercise_ids, assessment_exercise_ids, node_data = separate_exercise_types(node_data)
    html_exercise_path, translated_html_exercise_ids = retrieve_html_exercises(html_exercise_ids, lang)

    # now include only the assessment item resources that we need
    # all_assessment_resources = get_full_assessment_resource_list()
    # included_assessment_resources = filter_unneeded_assessment_resources(all_assessment_resources, exercise_data)

    # node_data = remove_untranslated_exercises(exercise_data, translated_html_exercise_ids, assessment_data)

    # node_data = remove_unavailable_topics(node_data)

    pack_metadata = generate_kalite_language_pack_metadata(lang, version, interface_catalog, content_catalog)

    bundle_language_pack(str(filename), node_data, interface_catalog, interface_catalog, pack_metadata)


def normalize_sublang_args(args):
    """
    Transform the command line arguments we have into something that conforms to the retrieve_language_resources interface.
    This mostly means using the given lang parameter as the default lang, overridable by the different sublang args.
    """
    return {
        "video_lang": args['--videolang'] or args['<lang>'],
        "content_lang": args['--contentlang'] or args['<lang>'],
        "interface_lang": args['--interfacelang'] or args['<lang>'],
        "subtitle_lang": args['--subtitlelang'] or args['<lang>'],
    }


def main():
    args = docopt(__doc__)

    assert args["ka-lite"], ("Sorry, content packs for non-KA Lite "
                             "software aren't implemented yet.")
    del args["ka-lite"]

    lang = args["<lang>"]
    version = args["<version>"]
    out = Path(args["--out"]) if args['--out'] else Path.cwd() / "{lang}.zip".format(lang=lang)

    sublangs = normalize_sublang_args(args)

    make_language_pack(lang, version, sublangs, out)


if __name__ == "__main__":
    main()