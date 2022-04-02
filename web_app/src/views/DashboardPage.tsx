import React, {useEffect, useState} from "react";
import api from "../api";
import {Container, Grid, Card, Typography, CardContent, CardMedia, Alert} from "@mui/material";
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

    return (
        <Card variant="outlined" sx={{maxWidth: 500, marginTop: '10px'}}>
            <CardMedia
                height={180}
                component="img"
                image="/static/images/model-3-21-white-background.jpg"
                alt="Tesla Model 3"
            />
            <CardContent>
                <Typography gutterBottom variant="h5" component="div">
                    Tesla Model 3
                </Typography>
                {solarChargeState.chargeState === 'Stopped' && <Alert severity="info">Not Charging</Alert>}
                {solarChargeState.chargeState === 'Charging' && <Alert severity="success">Currently Charging</Alert>}
                {solarChargeState.chargeState === 'Disconnected' && <Alert severity="error">Disconnected</Alert>}
                <Typography variant="body2" color="text.secondary" sx={{paddingTop: '10px', paddingBottom: '10px'}}>
                    <Grid container spacing={2}>
                        <Grid item xs={6} md={4}
                              sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                            Last Updated:
                        </Grid>
                        <Grid item xs={6} md={8} sx={{display: "flex", justifyContent: "flex-start"}}>
                            {solarChargeState.lastUpdated}
                        </Grid>
                        <Grid item xs={6} md={4}
                              sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                            Charge State:
                        </Grid>
                        <Grid item xs={6} md={8} sx={{display: "flex", justifyContent: "flex-start"}}>
                            {solarChargeState.chargeState}
                        </Grid>
                        <Grid item xs={6} md={4}
                              sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                            Current Load:
                        </Grid>
                        <Grid item xs={6} md={8} sx={{display: "flex", justifyContent: "flex-start"}}>
                            {(solarChargeState.currentLoad / 1000).toFixed(2)} kW
                        </Grid>
                        <Grid item xs={6} md={4}
                              sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                            Current Generation:
                        </Grid>
                        <Grid item xs={6} md={8} sx={{display: "flex", justifyContent: "flex-start"}}>
                            {(solarChargeState.currentGeneration / 1000).toFixed(2)} kW
                        </Grid>
                        <Grid item xs={6} md={4}
                              sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                            Spare Capacity:
                        </Grid>
                        <Grid item xs={6} md={8} sx={{display: "flex", justifyContent: "flex-start"}}>
                            {(solarChargeState.spareCapacity / 1000).toFixed(2)} kW
                        </Grid>
                        <Grid item xs={6} md={4}
                              sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                            Current Request:
                        </Grid>
                        <Grid item xs={6} md={8} sx={{display: "flex", justifyContent: "flex-start"}}>
                            {solarChargeState.chargeCurrentRequest} Amps
                        </Grid>
                        <Grid item xs={6} md={4}
                              sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                            Vehicle Charge:
                        </Grid>
                        <Grid item xs={6} md={8} sx={{display: "flex", justifyContent: "flex-start"}}>
                            {solarChargeState.vehicleCharge.toFixed(0)} %
                        </Grid>
                        <Grid item xs={6} md={4}
                              sx={{fontWeight: 'bold', display: "flex", justifyContent: "flex-start"}}>
                            Battery Charge:
                        </Grid>
                        <Grid item xs={6} md={8} sx={{display: "flex", justifyContent: "flex-start"}}>
                            {solarChargeState.batteryCharge.toFixed(0)} %
                        </Grid>
                    </Grid>
                </Typography>

                <Typography variant="body2" color="text.secondary" sx={{paddingTop: '10px'}}>
                    Spare Capacity (kW)
                </Typography>
                <LineChart width={430} height={250} data={data}>
                    <XAxis dataKey="minutes" minTickGap={100}/>
                    <YAxis domain={['dataMin - 2', 'dataMax + 2']}/>
                    <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
                    <Line type="monotone" dataKey="value" stroke="#8884d8"/>
                </LineChart>
                <Typography variant="body2" color="text.secondary">
                    Minutes ago
                </Typography>
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
        <Container maxWidth="sm">
            {solarChargeState ?
                <SolarChargeStatePanel solarChargeState={solarChargeState}/> : <LoadingPanel/>
            }
            <span>{errorMessage}</span>
        </Container>
    )
}

export default DashboardPage;
