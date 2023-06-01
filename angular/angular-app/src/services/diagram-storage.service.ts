import { Injectable } from "@angular/core";
import { FormGroup } from "@angular/forms";

@Injectable({
    providedIn: 'root'
})
export class DiagramStorageService {
    commonAppSettings = new CommonAppSettings()
    ghzsettings = new GHZSettings()
    constructor() {

    }

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

    advancedAppSettingsFormData

    getAppSettingsFormDataAdvanced() {
        return this.advancedAppSettingsFormData
    }
    setAppSettingsFormDataAdvanced(formData: any) {
        this.advancedAppSettingsFormData = formData
    }

    minimalAppSettingsFormData

    getAppSettingsFormDataMinimal() {
        return this.advancedAppSettingsFormData
    }
    setAppSettingsFormDataMinimal(formData: any) {
        this.advancedAppSettingsFormData = formData
    }

    getAppParameters(app_id, nodesSelection, appSettingsForm: FormGroup, e2e) {
        const appConfig =
        {
            1: {
                sender: nodesSelection.sender,
                receiver: nodesSelection.receiver,
                keyLength: Number(appSettingsForm.get('keyLength')?.value)
            },

            2: {
                sender: nodesSelection.sender,
                receiver: nodesSelection.receiver,
                startTime: 1e12,
                size: appSettingsForm.get('size')?.value,
                priority: 0,
                targetFidelity: e2e.targetFidelity,
                timeout: appSettingsForm.get('timeout')?.value + 'e12'
            }
            , 3: {
                sender: nodesSelection.sender,
                receiver: nodesSelection.receiver,
                amplitude1: appSettingsForm.get('amplitude1')?.value,
                amplitude2: appSettingsForm.get('amplitude2')?.value
            }, 4: {
                endnode1: appSettingsForm.get('endnode1')?.value,
                endnode2: appSettingsForm.get('endnode2')?.value,
                endnode3: appSettingsForm.get('endnode3')?.value,
                middlenode: appSettingsForm.get('middleNode')?.value,
            }, 5:
            {
                sender: nodesSelection.sender,
                receiver: nodesSelection.receiver,
                sequenceLength: appSettingsForm.get('sequenceLength')?.value,
                key: appSettingsForm.get('message')?.value
            }, 6:
            {
                sender: nodesSelection.sender,
                receiver: nodesSelection.receiver,
                sequenceLength: appSettingsForm.get('sequenceLength')?.value,
                message: appSettingsForm.get('message')?.value,
            }, 7:
            {
                sender: nodesSelection.sender,
                receiver: nodesSelection.receiver,
                message: appSettingsForm.get('message')?.value
            },
            8:
            {
                sender: nodesSelection.sender,
                receiver: nodesSelection.receiver,
                message1: appSettingsForm.get('message1')?.value,
                message2: appSettingsForm.get('message2')?.value,
                attack: ''
            }, 9:
            {
                sender: nodesSelection.sender,
                receiver: nodesSelection.receiver,
                message: appSettingsForm.get('inputMessage')?.value,
                attack: appSettingsForm.get('attack')?.value
            }, 10:
            {
                sender: {
                    node: nodesSelection.sender,
                    message: nodesSelection.message,
                    userID: `${nodesSelection.senderId}`,
                    num_check_bits: nodesSelection.numCheckBits,
                    num_decoy_photons: nodesSelection.numDecoy
                },
                receiver: {
                    node: nodesSelection.receiver,
                    userID: `${nodesSelection.receiverId}`
                },
                bell_type: `${nodesSelection.bellType}`,
                error_threshold: nodesSelection.errorThreshold,
                attack: nodesSelection.attack,
                channel: nodesSelection.channel
            }
        }
        return appConfig
    }

    


}
class CommonAppSettings {
    sender: string;
    receiver: string;
}
class GHZSettings {
    endNode1;
    endNode2;

    endNode3;

    middleNode;

}
class E91 {

    keyLength
}            