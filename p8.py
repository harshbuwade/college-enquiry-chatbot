isa={
    "bird":"animal",
    "dog":"animal",
    "sparrow":"bird"
}
has_property={
    "animal":"cells"
}
can_do={
    "bird":"fly",
    "dog":"bark"
}
def get_superclass(concept):
    return isa.get(concept,None)
def inherit_property(concept,propert_name):
    if concept in has_property and propert_name in has_property[concept]:
        return True
    #Check inheritance
    parent=get_superclass(concept)
    if parent:
        return inherit_property(parent,propert_name)
    return False

def inherit_ability(concept,ability):
    if concept in can_do and ability in can_do[concept]:
        return True
    parent=get_superclass(concept)
    if parent:
        return inherit_ability(parent,ability)
    return False
print("Is sparrow an animal ?")
print(inherit_property("sparrow","cells"))
print("Can sparrow fly ?")
print(inherit_ability("sparrow","fly"))
print("Can dog fly ?")
print(inherit_ability("dog","fly"))
print("Can sparrow bark ?")
print(inherit_ability("sparrow","bark"))
