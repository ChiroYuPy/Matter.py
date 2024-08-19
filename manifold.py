class Manifold:
    def __init__(self, bodyA, bodyB, normal, depth, contact1, contact2, contact_count):
        self.bodyA = bodyA
        self.bodyB = bodyB
        self.normal = normal
        self.depth = depth
        self.contact1 = contact1
        self.contact2 = contact2
        self.contact_count = contact_count