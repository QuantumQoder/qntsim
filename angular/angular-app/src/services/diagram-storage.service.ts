import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root'
})
export class DiagramStorageService {
    advancedDiagramModel: any

    setAdvancedDiagramModel(data) {
        this.advancedDiagramModel = data
    }

    getAdvancedDiagramModel() {
        return this.advancedDiagramModel
    }

    minimalValues: any
    getMinimalValues() {
        return this.minimalValues
    }
    setMinimalValues(minimalValues) {
        this.minimalValues = minimalValues
    }
}               