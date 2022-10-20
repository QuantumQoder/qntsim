import { Component, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-application-page',
  templateUrl: './application-page.component.html',
  styleUrls: ['./application-page.component.less']
})
export class ApplicationPageComponent implements OnInit {

  constructor(private _formBuilder: FormBuilder) { }
  form: any;
  //formArray: any
  ngOnInit(): void {
    this.form = this._formBuilder.group({
      formArray: this._formBuilder.array([this.buildGroup()])

    });

  }
  get formArray(): FormArray {
    return <FormArray>this.form.get('formArray');
  }
  buildGroup(): FormGroup {
    return this._formBuilder.group({
      name: [''],
      type: [''],
      noOfMemories: [''],
      memoryFrequency: [''],
      memoryExpiryTime: [''],
      memoryEfficiency: [''],
      memoryFidelity: ['']
    })
  }
  addTableRow() {
    this.formArray.push(this.buildGroup());
    //console.log(this.form.get('formArray').value);
  }
  deleteTableRow(index: any) {
    this.formArray.removeAt(index)
  }
}
