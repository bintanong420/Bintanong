"""Equivalent compact schema display; never substitutes the decoder's schema."""
from copy import deepcopy

_MAPS=('properties','$defs','definitions','patternProperties','dependentSchemas')
_SINGLE=('items','additionalProperties','not','if','then','else','contains','propertyNames')
_ARRAYS=('oneOf','anyOf','allOf','prefixItems')


def compact_for_prompt(schema):
    """Remove titles and repeated oneOf constraints already present on the parent.

    Only schema-bearing keywords are traversed. Values under const/enum/default
    are literal data, and property names such as 'title' must remain untouched.
    The original schema stays detached and is still supplied to decoding.
    """
    if not isinstance(schema,dict):
        return deepcopy(schema)
    result={}
    for key,value in schema.items():
        if key=='title':
            continue
        if key in _MAPS and isinstance(value,dict):
            result[key]={name:compact_for_prompt(child) for name,child in value.items()}
        elif key in _SINGLE and isinstance(value,dict):
            result[key]=compact_for_prompt(value)
        elif key in _ARRAYS and isinstance(value,list):
            result[key]=[compact_for_prompt(child) for child in value]
        else:
            result[key]=deepcopy(value)
    if isinstance(result.get('oneOf'),list):
        branches=[]
        for branch in result['oneOf']:
            if not isinstance(branch,dict):
                branches.append(branch)
                continue
            reduced={}
            for key,value in branch.items():
                if key=='properties' and isinstance(value,dict):
                    changes={name:child for name,child in value.items()
                        if name not in result.get('properties',{}) or child!=result['properties'][name]}
                    if changes:
                        reduced[key]=changes
                elif key not in result or value!=result[key]:
                    reduced[key]=value
            branches.append(reduced)
        result['oneOf']=branches
    return result
