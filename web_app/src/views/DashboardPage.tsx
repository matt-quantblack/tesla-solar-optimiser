import React, {useEffect, useState} from "react";
import api from "../api";
import {Container, Grid, Card, Typography, CardContent, Button, Alert, TextField, Box} from "@mui/material";
import {CartesianGrid, LineChart, Line, XAxis, YAxis} from "recharts";

// TODO: Split this out into different files / components
// TODO: Use Sass or styled components for styling

interface SolarChargeState {
    lastUpdated: string,
    chargeState: string,
    currentLoad: number,
    currentGeneration: number,
    spareCapacity: number,
    chargeCurrentRequest: number,
    vehicleCharge: number,
    batteryCharge: number,
    spareCapacityHistory: Array<number>
}

interface LoadingProps {
    message?: string
}

const LoadingPanel: React.FC<LoadingProps> = ({message = 'Loading ...'}) => <h1>{message}</h1>

interface SolarChargeStatePanelProps {
    solarChargeState: SolarChargeState
}

const SolarChargeStatePanel: React.FC<SolarChargeStatePanelProps> = ({solarChargeState}) => {

    const data = solarChargeState.spareCapacityHistory.map((value: any) => {
        return {
            minutes: ((((new Date().getTime()) / 1000) - value["timestamp"]) / 60).toFixed(0),
            value: (value['value'] / 1000).toFixed(1)
        };
    });
    // TODO: Work out the min and max here so it will dynamically update the chart when new data is updated.
    const last_update = ((new Date().getTime() - Date.parse(solarChargeState.lastUpdated)) / 1000 / 60).toFixed(
        0)
    return (
        <Card variant="outlined" sx={{width: 750, height: 450, marginTop: '10px'}}>
            <CardContent>
                <Grid container spacing={2}>
                    <Grid item xs={4}>
                        <img
                            style={{height: '70px'}}
                            src="/static/images/model-3-21-white-background.jpg"
                            alt="Tesla Model 3"/>
                    </Grid>
                    <Grid item xs={4} sx={{display: "block"}}>
                        <Typography gutterBottom variant="h5" component="div">
                            Tesla Model 3
                        </Typography>
                        <Typography variant="body2" color="text.secondary"
                                    sx={{paddingTop: '10px', paddingBottom: '10px'}}>
                            Last update {last_update} mins ago
                        </Typography>
                    </Grid>
                    <Grid item xs={4}>
                        {solarChargeState.chargeState === 'Stopped' &&
                            <Alert severity="info">Not Charging</Alert>}
                        {solarChargeState.chargeState === 'Charging' &&
                            <Alert severity="success">Currently Charging</Alert>}
                        {solarChargeState.chargeState === 'Disconnected' &&
                            <Alert severity="error">Disconnected</Alert>}
                    </Grid>
                    <Grid item xs={4}>
                        <Grid container spacing={2}>
                            <Grid item xs={6}
                                  sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                                Load:
                            </Grid>
                            <Grid item xs={6} sx={{display: "flex", justifyContent: "flex-start"}}>
                                {(solarChargeState.currentLoad / 1000).toFixed(2)} kW
                            </Grid>
                            <Grid item xs={6}
                                  sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                                Solar:
                            </Grid>
                            <Grid item xs={6} sx={{display: "flex", justifyContent: "flex-start"}}>
                                {(solarChargeState.currentGeneration / 1000).toFixed(2)} kW
                            </Grid>
                            <Grid item xs={6}
                                  sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                                Spare:
                            </Grid>
                            <Grid item xs={6} sx={{display: "flex", justifyContent: "flex-start"}}>
                                {(solarChargeState.spareCapacity / 1000).toFixed(2)} kW
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={4}>
                        <Grid container spacing={2}>
                            <Grid item xs={6}
                                  sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                                Current:
                            </Grid>
                            <Grid item xs={6} sx={{display: "flex", justifyContent: "flex-start"}}>
                                {solarChargeState.chargeCurrentRequest} Amps
                            </Grid>
                            <Grid item xs={6}
                                  sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                                Vehicle:
                            </Grid>
                            <Grid item xs={6} sx={{display: "flex", justifyContent: "flex-start"}}>
                                {solarChargeState.vehicleCharge.toFixed(0)} %
                            </Grid>
                            <Grid item xs={6}
                                  sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                                Battery:
                            </Grid>
                            <Grid item xs={6} sx={{display: "flex", justifyContent: "flex-start"}}>
                                {solarChargeState.batteryCharge.toFixed(0)} %
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={4}>
                        <Box sx={{display: "flex", justifyContent: "center", paddingBottom: '10px'}}>
                            <Button variant="contained" size="small" style={{marginRight: '10px'}}>Login</Button>
                            <Button variant={1 == 1 ? "contained" : "outlined"} size="small">Force Charge</Button>
                        </Box>
                        <TextField id="standard-basic" label="Min Vehicle Charge (%)" variant="standard" size="small"
                                   value={70}/>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary" sx={{paddingTop: '10px'}}>
                            Spare Capacity (kW)
                        </Typography>
                        <LineChart width={680} height={150} data={data}>
                            <XAxis dataKey="minutes" minTickGap={100}/>
                            <YAxis
                                domain={['dataMin - 2', 'dataMax + 2']}
                                tickFormatter={(number: number) => number.toFixed(1)}/>
                            <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
                            <Line type="monotone" dataKey="value" stroke="#8884d8"/>
                        </LineChart>
                        <Typography variant="body2" color="text.secondary">
                            Minutes ago
                        </Typography>
                    </Grid>
                </Grid>
            </CardContent>

        </Card>
    )
}

const DashboardPage = () => {

    const [solarChargeState, setSolarChargeState] = useState<null | SolarChargeState>(null);
    const [errorMessage, setErrorMessage] = useState(null);

    useEffect(() => {

        const getSolarChargeState = () => {
            api.getSolarChargeState().then(setSolarChargeState)
                .catch((http_error: any) => setErrorMessage(http_error));
        }

        getSolarChargeState()
        const interval = setInterval(() => getSolarChargeState(), 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <Container>
            {solarChargeState ?
                <SolarChargeStatePanel solarChargeState={solarChargeState}/> : <LoadingPanel/>
            }
            <span>{errorMessage}</span>
        </Container>
    )
}

export default DashboardPage;
