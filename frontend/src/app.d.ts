// app.d.ts is a special file in SvelteKit where you tell TypeScript about custom types your app uses. 
// For example, you can describe what properties exist on things like locals, session, or platform. This 
// helps TypeScript understand your code better and gives you helpful autocomplete and error checking when 
// you use those properties elsewhere in your project.


/// <reference types="@sveltejs/kit" />

declare namespace App {
    interface Locals {
        user: any | null;
        workspace: string;
    }
}
