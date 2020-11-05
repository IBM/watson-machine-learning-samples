# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#
library(shiny)
library(deSolve)

# SIR mathematical model
sir <- function(time, state, parameters) {
    with(as.list(c(state, parameters)), {
        dS <- -beta * S * I
        dI <- beta * S * I - gamma * I
        dR <- gamma * I

        return(list(c(dS, dI, dR)))
    })
}

# Define UI for app that draws SIR equations ----
ui <- fluidPage(

    # App title ----
    titlePanel("SIR MODEL EXAMPLE"),

    # Sidebar layout with input and output definitions ----
    sidebarLayout(

        # Sidebar panel for inputs ----
        sidebarPanel(

            # Input: Slider for time range ----
            sliderInput(inputId = "time_range",
                        label = "Time range:",
                        min = 10,
                        max = 1000,
                        value = 30),
            # Input: Slider for the value of 'beta' - infection ratio ----
            sliderInput(inputId = "infection_ratio",
                        label = "Infection ratio:",
                        min = 0.01,
                        max = 10.0,
                        value = 1.2),
            # Input: Slider for the value of 'gamma' - recover ratio ----
            sliderInput(inputId = "recover_ratio",
                        label = "Recover ratio:",
                        min = 0.01,
                        max = 1,
                        value = 0.1),
            # Input: Slider for the value of 'S' - Susceptible individuals percentage ----
            sliderInput(inputId = "susceptible_percentage",
                        label = "Susceptible percentage:",
                        min = 0.00001,
                        max = 0.99999,
                        value = 0.99999)
        ),

        # Main panel for displaying outputs ----
        mainPanel(

            # Output: SIR equations ----
            plotOutput(outputId = "sirPlot")
        )
    )
)

# Define server logic required to draw SIR equations ----
server <- function(input, output) {

    # 1. It is "reactive" and therefore should be automatically
    #    re-executed when inputs change
    # 2. Its output type is a plot
    output$sirPlot <- renderPlot({

        infected_number = 1 - input$susceptible_percentage

        init <- c(S = input$susceptible_percentage, I = infected_number, R = 0)
        parameters <- c(beta = input$infection_ratio, gamma = input$recover_ratio)
        times <- seq(0, input$time_range, by = 1)

        out <- as.data.frame(ode(y = init, times = times, func = sir, parms = parameters))
        out$time <- NULL

        matplot(times, out, type = "l", xlab = "Time", ylab = "Susceptibles, Infected and Recovered", main = "SIR Model", lwd = 1, lty = 1, bty = "l", col = 2:4)
        legend(40, 0.7, c("Susceptibles", "Infected", "Recovered"), pch = 1, col = 2:4)
    })

}

# Create Shiny app ----
shinyApp(ui = ui, server = server)