import json
import pygame
import event
import util

pygame.font.init()

font = pygame.font.Font(None, 36)

class Element:
    def __init__(self, etype, x, y):
        self.x          = x
        self.y          = y
        self.type       = etype
        self.event      = False
        self.display    = True

    def enable(self):
        self.display = True

    def disable(self):
        self.display = False


class Button(Element):
    def __init__(self, event, x, y, images):
        Element.__init__(self, "button", x, y)

        self.event  = event
        self.images = images
        self.w      = self.images["active"].get_width()
        self.h      = self.images["active"].get_height()

        self.state  = "inactive"

class Text(Element):
    def __init__(self, x, y):
        Element.__init__(self, "text", x, y)
        self.setText("")

    def setText(self, text):
        self.text   = font.render(text, 1, (200, 200, 200))
        self.w      = self.text.get_width()
        self.h      = self.text.get_height()



class UI:
    def __init__(self, uni, camera):
        self.uni = uni
        self.camera = camera

        self.elements = {} #id of element: element
        self.updates = {} #name of update function: update function, get called on each ui.update()
        self.setters = {} ##, get called once, on load
        self.usubs = [] #{"eid": eid, "name of update function": name of update function}
        self.enabled = True
        self.namesEnabled = True
        self.vectorsEnabled = False

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def enableNames(self):
        self.namesEnabled = True

    def disableNames(self):
        self.namesEnabled = False

    def enableVectors(self):
        self.vectorsEnabled = True

    def disableVectors(self):
        self.vectorsEnabled = False

    def addElement(self, e, eid):
        self.elements[eid] = e

    def getElement(self, eid):
        return self.elements[eid]

    def addUpdate(self, name, f):
        self.updates[name] = f

    def addSetter(self, name, f):
        self.setters[name] = f

    def subElementToUpdate(self, eid, name):
        self.usubs.append({"eid": eid, "name": name})

    def update(self):
        for sub in self.usubs:
            self.updates[sub["name"]](self.getElement(sub["eid"]))

    def load(self, string, path):
        """Loads a suite of UI elements described in a json string."""
        ui = json.loads(string)

        for eid in ui:
            if ui[eid]["type"] == "button":
                imagei = pygame.image.load(path + ui[eid]["inactive"]).convert()
                imagea = pygame.image.load(path + ui[eid]["active"]).convert()
                el = Button(ui[eid]["event"], ui[eid]["x"], ui[eid]["y"], {"inactive": imagei, "active": imagea})

            if ui[eid]["type"] == "text":
                el = Text(ui[eid]["x"], ui[eid]["y"])

                if ui[eid].has_key("text"):
                    el.setText(ui[eid]["text"])

            if ui[eid].has_key("update"):
                self.subElementToUpdate(eid, ui[eid]["update"])

            self.addElement(el, eid)

            if ui[eid].has_key("set"):
                self.setters[ui[eid]["set"]](el)

    def down(self, pos):
        if not self.enabled:
            return

        for e in self.elements.itervalues():
            if (pos[0] > e.x and pos[0] < e.x + e.w and pos[1] > e.y and pos[1] < e.y + e.h):
                e.state = "active"

    def up(self, pos):
        if not self.enabled:
            return

        for e in self.elements.itervalues():
            e.state = "inactive"

            if (pos[0] > e.x and pos[0] < e.x + e.w and pos[1] > e.y and pos[1] < e.y + e.h) and e.event:
                event.pub(e.event, None)

        centered = False
        for b in self.uni.bodies.itervalues():
            sp = util.toScreen(b.position, self.camera)

            if (sp[0] - pos[0])**2 + (sp[1] - pos[1])**2 < (b.r*self.camera.zoom)**2:
                self.camera.center(b)
                centered = True

        if not centered:
            self.camera.release()

    def checkMouse(self, pos):
        pass
