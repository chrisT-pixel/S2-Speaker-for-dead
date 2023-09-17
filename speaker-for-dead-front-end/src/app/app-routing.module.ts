import { NgModule } from '@angular/core';
import { CustomClonesComponent } from './custom-clones/custom-clones.component'
import { InteractComponent } from './interact/interact.component'
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', component: InteractComponent }, // Home page
  { path: 'custom-clones', component: CustomClonesComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
