import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { WebSocketService } from './websocket.service';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { InteractComponent } from './interact/interact.component';
import { FormsModule } from '@angular/forms'; // <-- NgModel lives here
import { HttpClientModule } from '@angular/common/http'; // Import HttpClientModule
import { SocketIoModule } from 'ngx-socket-io';



@NgModule({
  declarations: [
    AppComponent,
    InteractComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    SocketIoModule.forRoot({ url: 'http://localhost:5000' }),
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
