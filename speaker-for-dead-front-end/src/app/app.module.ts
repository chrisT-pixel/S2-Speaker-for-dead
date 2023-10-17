import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { InteractComponent } from './interact/interact.component';
import { FormsModule } from '@angular/forms'; 
import { HttpClientModule } from '@angular/common/http'; 
import { SocketIoModule } from 'ngx-socket-io';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CustomClonesComponent } from './custom-clones/custom-clones.component';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatIconModule} from '@angular/material/icon';
import { CloneModalComponent } from './clone-modal/clone-modal.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { VoiceRecorderComponent } from './voice-recorder/voice-recorder.component';
import { PhotoCaptureComponent } from './photo-capture/photo-capture.component';
import { VoiceReconComponent } from './voice-recon/voice-recon.component';


@NgModule({
  declarations: [
    AppComponent,
    InteractComponent,
    CustomClonesComponent,
    CloneModalComponent,
    VoiceRecorderComponent,
    PhotoCaptureComponent,
    VoiceReconComponent,

  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    SocketIoModule.forRoot({ url: 'http://localhost:5000' }),
    HttpClientModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatIconModule,
    NgbModule,

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
