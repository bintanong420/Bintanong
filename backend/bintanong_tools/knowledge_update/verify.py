from pathlib import Path

from .build import load_package
from .prepare import load_packet
from .review import ReviewSession


def verify(root: Path, *, packet_root: Path | None = None) -> dict:
    package = load_package(root)
    if packet_root is not None:
        packet = load_packet(packet_root)
        with ReviewSession(packet_root, 'Package verifier') as review:
            export = review.export()
        if (package['manifest']['packet_id'] != packet['packet_id']
                or export != package['recipe']['export']):
            raise ValueError('package is stale relative to the packet review revision')
    return {'verified': True, 'candidate_only': True, 'activation_eligible': False,
            'package_id': package['manifest']['package_id'], 'chunks': len(package['chunks']),
            'scope': 'selected source/review/configuration bindings; not institutional approval or answer accuracy',
            'context_budget_method': 'conservative sum of exact prefixed chunk token counts'}
